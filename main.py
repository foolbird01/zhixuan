"""
主程序入口 - FastAPI Web 应用
就像餐厅的"前台"，负责接待客户、派单、结账

功能：
1. 上传任务样本（网页表单）
2. 选择要测试的模型
3. 启动评估（后台运行）
4. 查看/下载报告
"""

import os
import sys
import json
import uuid
from datetime import datetime

# 修复 Windows GBK 编码问题：强制 stdout 使用 utf-8
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from typing import List, Dict, Any, Optional
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from pydantic import BaseModel

# 导入我们自己的模块
from config import AVAILABLE_MODELS, DEFAULT_WEIGHTS, JUDGE_MODEL
from models import (
    TaskSample, TaskBatch, ModelConfig,
    BenchmarkRequest, BenchmarkResponse, BenchmarkReport
)
from api_client import ModelAPIClient
from evaluator import ModelEvaluator
from report_generator import ReportGenerator


# ==================== 初始化 FastAPI 应用 ====================
app = FastAPI(
    title="智选 - AI模型选型平台",
    description="企业大模型成本效益分析与自动化选型平台",
    version="1.0.0",
)

# 挂载静态文件目录（CSS、JS、图片等）
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 模板引擎（用来渲染HTML页面）
templates = Jinja2Templates(directory="templates")


# ==================== 全局变量（简单存储，生产环境用数据库）====================
# 存储任务批次
task_batches: Dict[str, TaskBatch] = {}

# 存储评估报告
reports: Dict[str, BenchmarkReport] = {}

# 存储评估状态（用来显示进度）
evaluation_status: Dict[str, Dict] = {}


# ==================== 数据模型（给Web API用）====================
class UploadTaskBatchRequest(BaseModel):
    """上传任务批次的请求"""
    name: str
    description: Optional[str] = ""


class EvaluationRequest(BaseModel):
    """启动评估的请求"""
    model_config = {"protected_namespaces": ()}  # 解决 Pydantic v2 的 model_ 前缀冲突
    
    batch_id: str
    model_names: List[str]
    weights: Optional[Dict[str, float]] = None
    judge_model: Optional[str] = None


# ==================== 工具函数 ====================
def load_sample_tasks() -> TaskBatch:
    """加载示例任务（如果没有上传自己的任务，可以用示例）"""
    sample_path = Path("data/sample_tasks.json")
    
    if not sample_path.exists():
        # 如果示例文件不存在，创建一个默认的
        sample_tasks = TaskBatch(
            batch_id="sample_" + str(uuid.uuid4())[:8],
            name="示例任务 - 客服问答测试集",
            description="包含10个客服场景的测试问题，用来演示平台功能",
            tasks=[
                TaskSample(
                    id="task_001",
                    task_type="qa",
                    instruction="用户问：'你们店支持7天无理由退货吗？' 请按照优质客服的标准回复。",
                    input_text="",
                    expected_keywords=["7天", "无理由", "退货", "支持"],
                ),
                TaskSample(
                    id="task_002",
                    task_type="qa",
                    instruction="用户投诉：'我买的东西有质量问题，你们怎么处理？' 请友好地回复。",
                    input_text="",
                    expected_keywords=["抱歉", "质量", "处理", "联系"],
                ),
                TaskSample(
                    id="task_003",
                    task_type="summarization",
                    instruction="请把以下客服通话记录总结成3个要点：",
                    input_text="客户：你们这个产品怎么用啊？\n客服：您好，这个产品首先按电源键开机，然后选择模式...\n客户：那电池能用多久？\n客服：满电情况下可以使用约8小时...\n客户：好的我知道了谢谢。\n客服：不客气，有问题随时联系我们。",
                    expected_keywords=["产品使用", "电池续航", "客服态度"],
                ),
                # 更多示例任务...
                TaskSample(
                    id="task_004",
                    task_type="code_generation",
                    instruction="写一个Python函数，输入一个列表，返回里面所有偶数的和。",
                    input_text="",
                    reference_output="```python\ndef sum_even_numbers(numbers):\n    return sum(n for n in numbers if n % 2 == 0)\n```",
                ),
                TaskSample(
                    id="task_005",
                    task_type="translation",
                    instruction="把以下中文翻译成英文：",
                    input_text="我们公司致力于为客户提供最优质的服务，以满足他们的需求。",
                    expected_keywords=["provide", "customers", "quality", "services"],
                ),
            ],
        )
        
        # 保存示例文件
        sample_path.parent.mkdir(exist_ok=True)
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(sample_tasks.model_dump(), f, ensure_ascii=False, indent=2)
        
        return sample_tasks
    
    # 从文件加载
    with open(sample_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        # 兼容：如果没有 batch_id，自动生成一个
        if "batch_id" not in data:
            data["batch_id"] = "sample_" + str(uuid.uuid4())[:8]
        return TaskBatch(**data)


# ==================== 路由定义 ====================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    首页 - 展示平台功能入口
    
    就像餐厅的"菜单首页"，告诉客户能点什么菜
    """
    return templates.get_template("index.html").render(
        request=request,
        available_models=list(AVAILABLE_MODELS.keys()),
    )


@app.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """上传任务页面"""
    return templates.get_template("upload.html").render(
        request=request,
    )


@app.post("/api/upload-tasks")
async def upload_tasks(
    name: str = Form(...),
    description: str = Form(""),
    file: UploadFile = File(...),
):
    """
    上传任务文件（JSON格式）
    
    就像客户"点单"，把要测的题目上传上来
    """
    try:
        # 读取上传的文件
        content = await file.read()
        data = json.loads(content)
        
        # 兼容两种格式：{"tasks": [...]} 或纯数组 [...]
        if "tasks" in data:
            tasks_list = data["tasks"]
        elif isinstance(data, list):
            tasks_list = data
        else:
            raise HTTPException(status_code=400, detail="JSON 格式错误：需要 {\"tasks\": [...]} 格式或纯数组格式")
        
        # 创建任务批次
        batch = TaskBatch(
            batch_id="batch_" + str(uuid.uuid4())[:8],
            name=name,
            description=description,
            tasks=[TaskSample(**t) for t in tasks_list],
        )
        
        # 保存
        task_batches[batch.batch_id] = batch
        
        return JSONResponse({
            "status": "success",
            "batch_id": batch.batch_id,
            "task_count": len(batch.tasks),
            "message": f"成功上传 {len(batch.tasks)} 个任务",
        })
    
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="JSON 格式错误，请检查文件")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")


@app.get("/api/available-models")
async def get_available_models():
    """获取可用的模型列表（给前端显示，按国内/国外分类）"""
    models_info = []
    for name, config in AVAILABLE_MODELS.items():
        models_info.append({
            "name": name,
            "display_name": name,
            "provider": config["provider"],
            "price_input": config["price_per_1k_input"],
            "price_output": config["price_per_1k_output"],
            "speed": config["speed"],
            "region": config.get("region", "unknown"),  # china 或 overseas
        })
    return {"models": models_info}


@app.post("/api/start-evaluation")
async def start_evaluation(request: EvaluationRequest, background_tasks: BackgroundTasks):
    """
    启动评估任务（后台运行）
    
    就像客户"下单"，后台开始做菜
    """
    # 验证 batch_id
    if request.batch_id not in task_batches:
        # 如果没找到（包括示例任务的 'sample' 标识），加载示例任务
        batch = load_sample_tasks()
        # 关键修复：无论传入什么 batch_id，只要不在字典里就用加载的示例任务
        task_batches[batch.batch_id] = batch
        request.batch_id = batch.batch_id  # 使用实际的 batch_id
    
    batch = task_batches[request.batch_id]
    
    # 验证模型名称
    invalid_models = [m for m in request.model_names if m not in AVAILABLE_MODELS]
    if invalid_models:
        raise HTTPException(status_code=400, detail=f"未知模型：{', '.join(invalid_models)}")
    
    # 创建报告ID
    report_id = "report_" + str(uuid.uuid4())[:8]
    
    # 初始化状态
    evaluation_status[report_id] = {
        "status": "running",
        "progress": 0,
        "total_tasks": len(batch.tasks),
        "completed_tasks": 0,
        "message": "评估任务已提交，正在后台运行...",
    }
    
    # 添加后台任务
    background_tasks.add_task(
        run_evaluation,
        report_id=report_id,
        batch=batch,
        model_names=request.model_names,
        weights=request.weights or DEFAULT_WEIGHTS,
        judge_model=request.judge_model or JUDGE_MODEL,
    )
    
    return {
        "status": "accepted",
        "report_id": report_id,
        "message": "评估任务已启动，请稍后查询进度",
    }


def run_evaluation(
    report_id: str,
    batch: TaskBatch,
    model_names: List[str],
    weights: Dict[str, float],
    judge_model: str,
):
    """
    后台运行评估任务（同步执行，由 background_tasks 在线程池中运行）
    
    这是核心流程！
    1. 初始化客户端
    2. 对每个任务，调用所有候选模型
    3. 评估质量（LLM-as-Judge）
    4. 计算综合得分
    5. 生成报告
    """
    try:
        # ========== 第一步：初始化 ==========
        status = evaluation_status[report_id]
        status["message"] = "正在初始化 API 客户端..."
        
        api_client = ModelAPIClient()
        evaluator = ModelEvaluator(api_client)
        report_gen = ReportGenerator()
        
        
        # ========== 第二步：准备模型配置 ==========
        status["message"] = "正在准备模型配置..."
        
        model_configs = []
        for name in model_names:
            config = AVAILABLE_MODELS[name]
            model_configs.append(ModelConfig(
                model_name=name,
                display_name=name,
                provider=config["provider"],
                model_id=config["model_id"],
                api_base=config.get("api_base"),
                price_per_1k_input=config["price_per_1k_input"],
                price_per_1k_output=config["price_per_1k_output"],
                context_window=config["context_window"],
                speed=config["speed"],
            ))
        
        
        # ========== 第三步：逐个任务评估 ==========
        task_results = []
        
        for i, task in enumerate(batch.tasks):
            status["message"] = f"正在评估任务 {i+1}/{len(batch.tasks)}: {task.id}"
            
            # 调用所有候选模型
            model_responses = {}
            for model_config in model_configs:
                try:
                    response = api_client.call_model(
                        model_config=model_config,
                        instruction=task.instruction,
                        input_text=task.input_text,
                        max_tokens=1000,
                    )
                    model_responses[model_config.model_name] = response
                except Exception as e:
                    print(f"⚠️ 模型 {model_config.model_name} 调用失败: {e}")
                    # 创建一个失败的响应
                    from models import ModelResponse
                    model_responses[model_config.model_name] = ModelResponse(
                        model_name=model_config.model_name,
                        task_id=task.id,
                        success=False,
                        error_message=str(e),
                    )
            
            # 评估这个任务
            result = evaluator.evaluate_task(
                task_sample=task,
                model_responses=model_responses,
                weights=weights,
            )
            task_results.append(result)
            
            # 更新进度
            status["completed_tasks"] = i + 1
            status["progress"] = int((i + 1) / len(batch.tasks) * 100)
        
        
        # ========== 第四步：生成汇总统计 ==========
        status["message"] = "正在生成汇总统计..."
        
        summary_stats = evaluator.generate_summary_stats(task_results)
        
        
        # ========== 第五步：生成推荐结论 ==========
        status["message"] = "正在生成推荐结论..."
        
        # 找到综合得分最高的模型
        best_overall = max(
            summary_stats.items(),
            key=lambda x: x[1]["avg_comprehensive_score"]
        )[0] if summary_stats else ""
        
        # 找到性价比最高的模型（质量/成本比）
        best_cost_effective = ""
        best_ratio = 0
        for model, stats in summary_stats.items():
            if stats["total_cost"] > 0:
                ratio = stats["avg_quality_score"] / (stats["total_cost"] + 0.0001)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_cost_effective = model
        
        recommendation = {
            "best_overall": best_overall,
            "best_cost_effective": best_cost_effective,
            "reasoning": f"根据综合评估（质量占50%、成本占30%、速度占20%），"
                         f"**{best_overall}** 表现最优。"
                         f"如果预算有限，推荐使用 **{best_cost_effective}**，性价比最高。",
        }
        
        
        # ========== 第六步：成本预测 ==========
        status["message"] = "正在生成成本预测..."
        
        cost_projection = {}
        call_volumes = [1000, 5000, 10000, 50000, 100000]
        
        for model_name in model_names:
            if model_name in summary_stats:
                avg_cost = summary_stats[model_name]["total_cost"] / max(summary_stats[model_name]["tasks_tested"], 1)
                projections = []
                for volume in call_volumes:
                    projections.append({
                        "monthly_calls": volume,
                        "monthly_cost": round(avg_cost * volume, 2),
                    })
                cost_projection[model_name] = projections
        
        
        # ========== 第七步：生成报告 ==========
        status["message"] = "正在生成报告..."
        
        report = BenchmarkReport(
            report_id=report_id,
            report_title="AI模型选型与投资回报分析报告",
            created_at=datetime.now().isoformat(),
            batch_name=batch.name,
            models_tested=model_names,
            total_tasks=len(batch.tasks),
            task_results=task_results,
            summary_stats=summary_stats,
            recommendation=recommendation,
            cost_projection=cost_projection,
        )
        
        # 保存报告
        reports[report_id] = report
        
        # 生成报告文件（Markdown + HTML）
        report_gen.generate_report(report, formats=["markdown", "html"])
        
        
        # ========== 完成！==========
        status["status"] = "completed"
        status["progress"] = 100
        status["message"] = "评估完成！报告已生成。"
        status["report"] = report.model_dump()
        
        print(f"✅ 评估完成！报告ID: {report_id}")
    
    except Exception as e:
        # 如果出错，更新状态
        evaluation_status[report_id]["status"] = "failed"
        evaluation_status[report_id]["message"] = f"评估失败：{str(e)}"
        print(f"❌ 评估失败: {e}")


@app.get("/api/evaluation-status/{report_id}")
async def get_evaluation_status(report_id: str):
    """查询评估进度 - 返回友好JSON，不抛异常"""
    if report_id not in evaluation_status:
        # 返回友好格式而不是抛404，前端轮询时不会报错
        return {
            "status": "not_found",
            "progress": 0,
            "message": "报告不存在或已过期，请重新启动评估",
            "report_id": report_id,
        }
    return evaluation_status[report_id]


@app.get("/api/report/{report_id}")
async def get_report(report_id: str):
    """获取评估报告（JSON格式）- 返回友好JSON"""
    if report_id not in reports:
        return JSONResponse(
            status_code=404,
            content=json.dumps({"error": "报告不存在", "report_id": report_id}, ensure_ascii=False)
        )
    return reports[report_id].model_dump()


@app.get("/download/report/{report_id}")
async def download_report(report_id: str, format: str = "markdown"):
    """
    下载报告文件
    
    format: markdown / html / pdf
    """
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    # 根据格式找文件
    if format == "markdown":
        file_path = Path("reports") / f"{report_id}.md"
    elif format == "html":
        file_path = Path("reports") / f"{report_id}.html"
    elif format == "pdf":
        file_path = Path("reports") / f"{report_id}.pdf"
    else:
        raise HTTPException(status_code=400, detail="不支持的格式")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="报告文件不存在")
    
    return FileResponse(
        path=file_path,
        filename=file_path.name,
        media_type="application/octet-stream",
    )


@app.get("/results/{report_id}", response_class=HTMLResponse)
async def results_page(request: Request, report_id: str):
    """查看评估结果页面"""
    if report_id not in reports:
        raise HTTPException(status_code=404, detail="报告不存在")
    
    return templates.get_template("results.html").render(
        request=request,
        report=reports[report_id],
    )


# ==================== 启动命令 ====================
if __name__ == "__main__":
    import uvicorn
    
    print("=" * 60)
    print("智选 - AI模型选型平台")
    print("=" * 60)
    print("\n启动说明：")
    print("  1. 请确保已安装依赖：pip install -r requirements.txt")
    print("  2. 请确保 .env 文件已配置 API Key")
    print("  3. 启动后访问：http://localhost:8000")
    print("\n配置说明：")
    print("  在项目根目录创建 .env 文件，写入：")
    print("  OPENAI_API_KEY=sk-xxxxxxxxxxxx")
    print("  ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx")
    print("  DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx")
    print("  DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx")
    print("\n" + "=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
评估器 - 负责评估模型输出质量
就像考试的"阅卷老师"，给每个模型的回答打分

包含三个维度：
1. 成本评估 - 花了多少钱
2. 速度评估 - 响应有多快
3. 质量评估 - 回答得好不好（用 LLM-as-Judge，让强大模型当评委）
"""

import sys
import time
from typing import List, Dict, Any, Optional

# 修复 Windows GBK 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from config import JUDGE_MODEL, QUALITY_SCORE_THRESHOLDS, DEFAULT_WEIGHTS, AVAILABLE_MODELS
from models import ModelResponse, QualityScore, TaskEvaluationResult
from api_client import ModelAPIClient


class ModelEvaluator:
    """
    模型评估器
    
    为什么需要 "LLM-as-Judge"？
    - 传统评估：用 BLEU、ROUGE 等指标，但这些指标跟人类判断相关性不高
    - LLM-as-Judge：让 GPT-4o 当评委，给模型回答打分（1-10分）
    - 研究表明：GPT-4o 的评分跟人类评分相关性很高（>0.8）
    - 成本：用 gpt-4o-mini 当评委，每1000条评分约 $0.5，很便宜
    """
    
    def __init__(self, api_client: ModelAPIClient):
        """初始化评估器，需要传入 API 客户端（用来调用评委模型）"""
        self.api_client = api_client
        self.judge_model_config = self._get_model_config(JUDGE_MODEL)
    
    
    def _get_model_config(self, model_name: str):
        """从 config.py 读取模型配置"""
        from config import AVAILABLE_MODELS
        if model_name not in AVAILABLE_MODELS:
            raise ValueError(f"模型 {model_name} 未在 config.py 中配置")
        
        config = AVAILABLE_MODELS[model_name]
        from models import ModelConfig
        return ModelConfig(
            model_name=model_name,
            display_name=model_name,
            provider=config["provider"],
            model_id=config["model_id"],
            api_base=config.get("api_base"),
            price_per_1k_input=config["price_per_1k_input"],
            price_per_1k_output=config["price_per_1k_output"],
            context_window=config["context_window"],
            speed=config["speed"],
        )
    
    
    def evaluate_task(
        self,
        task_sample,
        model_responses: Dict[str, ModelResponse],
        weights: Dict[str, float] = None,
    ) -> TaskEvaluationResult:
        """
        评估单个任务的所有模型回复
        
        参数：
        - task_sample: 任务样本（题目）
        - model_responses: 各个模型的回复 {模型名: 回复内容}
        - weights: 评估维度权重（成本、速度、质量的占比）
        
        返回：
        - TaskEvaluationResult: 包含所有的评估结果
        """
        
        if weights is None:
            weights = DEFAULT_WEIGHTS
        
        # 初始化结果对象
        result = TaskEvaluationResult(
            task_id=task_sample.id,
            task_type=task_sample.task_type,
            instruction=task_sample.instruction,
            input_text=task_sample.input_text,
            reference_output=task_sample.reference_output,
        )
        
        # ========== 第一步：收集所有模型的回复 ==========
        result.responses = {name: resp for name, resp in model_responses.items()}
        
        # ========== 第二步：质量评估（LLM-as-Judge）====================
        quality_scores = {}
        for model_name, response in model_responses.items():
            if not response.success:
                # 如果模型调用失败，给0分
                quality_scores[model_name] = QualityScore(
                    model_name=model_name,
                    task_id=task_sample.id,
                    overall_score=0.0,
                    accuracy=0.0,
                    relevance=0.0,
                    completeness=0.0,
                    readability=0.0,
                    reasoning="模型调用失败，无法评估",
                )
            else:
                # 调用评委模型打分
                score = self._judge_quality(task_sample, response.output_text)
                quality_scores[model_name] = score
        
        result.quality_scores = {name: score for name, score in quality_scores.items()}
        
        # ========== 第三步：计算综合得分 ==========
        # 综合得分 = 成本得分×30% + 速度得分×20% + 质量得分×50%
        # （权重可以调整）
        
        comprehensive_scores = {}
        for model_name in model_responses.keys():
            cost_score = self._calculate_cost_score(model_responses[model_name])
            speed_score = self._calculate_speed_score(model_responses[model_name])
            quality_score = quality_scores[model_name].overall_score
            
            # 加权平均（所有分数都归一化到 0-10 分制）
            final_score = (
                cost_score * weights["cost"] * 10 +     # 成本越低分越高，需要反转
                speed_score * weights["speed"] * 10 +
                quality_score * weights["quality"]
            )
            comprehensive_scores[model_name] = round(final_score, 2)
        
        result.comprehensive_scores = comprehensive_scores
        
        return result
    
    
    def _judge_quality(self, task_sample, model_output: str) -> QualityScore:
        """
        用评委模型评估质量（LLM-as-Judge）
        
        评分维度：
        1. 准确性（Accuracy）：回答是否正确
        2. 相关性（Relevance）：是否回答了问题
        3. 完整性（Completeness）：是否覆盖所有要点
        4. 可读性（Readability）：是否通顺易懂
        
        总分 = 四个维度的平均分（1-10分）
        """
        
        # 构造评委的"阅卷标准"
        judge_prompt = f"""你是一位专业的AI模型评估专家。请对以下AI模型的回答进行评分。

【任务指令】
{task_sample.instruction}

【输入内容】
{task_sample.input_text if task_sample.input_text else "（无输入内容）"}

【模型回答】
{model_output}

【参考答案（如果有）】
{task_sample.reference_output if task_sample.reference_output else "（无参考答案）"}

【评分标准】
请从以下四个维度打分（每维度 1-10 分）：

1. 准确性（Accuracy）：回答是否准确、有无事实错误？
2. 相关性（Relevance）：是否直接回答了问题？有没有答非所问？
3. 完整性（Completeness）：是否覆盖了所有要点？有没有遗漏重要信息？
4. 可读性（Readability）：表达是否清晰、通顺、易懂？

【输出格式】
请严格按照以下JSON格式输出（不要输出其他内容）：
{{
    "accuracy": 8,
    "relevance": 9,
    "completeness": 7,
    "readability": 8,
    "reasoning": "回答准确，直接解决了用户问题，但缺少了XXX部分..."
}}
"""
        
        try:
            # 调用评委模型
            judge_response = self.api_client.call_model(
                model_config=self.judge_model_config,
                instruction=judge_prompt,
                max_tokens=500,
            )
            
            # 解析评委的回复（期望是JSON格式）
            import json, re
            output_text = judge_response.output_text.strip()
            
            # 如果回复被 ```json ``` 包裹，先去掉
            if output_text.startswith("```"):
                output_text = output_text.split("\n", 1)[1].rsplit("\n", 1)[0]
            
            scores = None
            try:
                scores = json.loads(output_text)
            except json.JSONDecodeError:
                # 尝试用正则提取 JSON 对象
                json_match = re.search(r'\{[^{}]*"accuracy"[^{}]*\}', output_text)
                if json_match:
                    try:
                        scores = json.loads(json_match.group())
                    except:
                        pass
            
            if not scores:
                # 最后手段：用正则逐个提取分数
                scores = {}
                for dim in ["accuracy", "relevance", "completeness", "readability"]:
                    m = re.search(rf'"{dim}"\s*:\s*(\d+(?:\.\d+)?)', output_text)
                    if m:
                        scores[dim] = float(m.group(1))
                    else:
                        scores[dim] = 5.0  # 默认及格分
            
            # 计算总分（四个维度的平均）
            overall = (scores["accuracy"] + scores["relevance"] + 
                      scores["completeness"] + scores["readability"]) / 4
            
            return QualityScore(
                model_name="",  # 会在调用处填充
                task_id=task_sample.id,
                overall_score=round(overall, 1),
                accuracy=scores["accuracy"],
                relevance=scores["relevance"],
                completeness=scores["completeness"],
                readability=scores["readability"],
                reasoning=scores.get("reasoning", ""),
            )
        
        except Exception as e:
            print(f"⚠️ 质量评估失败: {e}")
            # 如果评委模型失败，返回默认分数
            return QualityScore(
                model_name="",
                task_id=task_sample.id,
                overall_score=5.0,  # 默认给5分（及格）
                accuracy=5.0,
                relevance=5.0,
                completeness=5.0,
                readability=5.0,
                reasoning=f"评委模型评估失败: {str(e)}",
            )
    
    
    def _calculate_cost_score(self, response: ModelResponse) -> float:
        """
        计算成本得分（0-1之间，越高越好）
        
        得分逻辑：
        - 成本越低，得分越高
        - 用 sigmoid 函数归一化（让分数更平滑）
        """
        if response.cost == 0:
            return 1.0  # 免费的就是满分
        
        # 归一化：成本 < $0.01 得高分（0.8-1.0），成本 > $0.1 得低分（0-0.3）
        # 用指数函数：score = exp(-cost * 100)
        import math
        score = math.exp(-response.cost * 100)
        return round(score, 3)
    
    
    def _calculate_speed_score(self, response: ModelResponse) -> float:
        """
        计算速度得分（0-1之间，越高越好）
        
        得分逻辑：
        - < 1秒：0.9-1.0分
        - 1-3秒：0.7-0.9分
        - 3-5秒：0.5-0.7分
        - > 5秒：0-0.5分
        """
        latency = response.latency
        
        if latency <= 1:
            return 1.0
        elif latency <= 3:
            return 0.9
        elif latency <= 5:
            return 0.7
        elif latency <= 10:
            return 0.5
        else:
            return 0.3
    
    
    def evaluate_batch(
        self,
        task_batch,
        model_responses_list: List[Dict[str, ModelResponse]],
        weights: Dict[str, float] = None,
    ) -> List[TaskEvaluationResult]:
        """
        批量评估多个任务
        
        参数：
        - task_batch: 任务批次
        - model_responses_list: 每个任务的模型回复列表
          [{模型名: ModelResponse}, ...]
        - weights: 评估权重
        
        返回：
        - 每个任务的评估结果列表
        """
        results = []
        
        for i, task in enumerate(task_batch.tasks):
            print(f"📊 评估任务 {i+1}/{len(task_batch.tasks)}: {task.id}")
            
            result = self.evaluate_task(
                task_sample=task,
                model_responses=model_responses_list[i],
                weights=weights,
            )
            results.append(result)
        
        return results
    
    
    def generate_summary_stats(self, results: List[TaskEvaluationResult]) -> Dict[str, Any]:
        """
        生成汇总统计
        
        返回：
        - 各个模型的平均得分、总成本、平均响应时间等
        """
        import pandas as pd
        
        # 转成 DataFrame 方便计算
        rows = []
        for result in results:
            for model_name in result.comprehensive_scores.keys():
                row = {
                    "model": model_name,
                    "task_id": result.task_id,
                    "comprehensive_score": result.comprehensive_scores[model_name],
                    "quality_score": result.quality_scores[model_name].overall_score if model_name in result.quality_scores else 0,
                    "cost": result.responses[model_name].cost if model_name in result.responses else 0,
                    "latency": result.responses[model_name].latency if model_name in result.responses else 0,
                }
                rows.append(row)
        
        df = pd.DataFrame(rows)
        
        # 按模型汇总
        summary = df.groupby("model").agg({
            "comprehensive_score": ["mean", "std"],
            "quality_score": ["mean", "std"],
            "cost": ["sum", "mean"],
            "latency": ["mean", "std"],
        }).round(3)
        
        # 转成字典格式（方便JSON序列化）
        result_dict = {}
        for model in df["model"].unique():
            model_df = df[df["model"] == model]
            result_dict[model] = {
                "avg_comprehensive_score": round(model_df["comprehensive_score"].mean(), 2),
                "avg_quality_score": round(model_df["quality_score"].mean(), 2),
                "total_cost": round(model_df["cost"].sum(), 4),
                "avg_latency": round(model_df["latency"].mean(), 2),
                "tasks_tested": len(model_df),
            }
        
        return result_dict

"""
数据模型定义 - 用 Pydantic 定义数据结构
就像餐厅的"点菜单格式"，规定什么样的数据才是合法的
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


# ==================== 任务类型枚举 ====================
class TaskType(str, Enum):
    """任务类型 - 企业常见的AI任务"""
    QA = "qa"                        # 问答（客服场景）
    SUMMARIZATION = "summarization"  # 总结/摘要
    CODE_GENERATION = "code_generation"  # 代码生成
    TRANSLATION = "translation"       # 翻译
    REPORT_GENERATION = "report_generation"  # 报告生成
    CLASSIFICATION = "classification" # 分类


# ==================== 任务数据模型 ====================
class TaskSample(BaseModel):
    """单个任务样本 - 就像考试的一道题"""
    id: str = Field(..., description="题目ID，比如 'task_001'")
    task_type: TaskType = Field(..., description="任务类型")
    instruction: str = Field(..., description="任务指令，比如'请把下面这段话总结成100字'")
    input_text: str = Field("", description="输入文本，比如要总结的那段话")
    reference_output: Optional[str] = Field(None, description="参考答案（可选），用来对比质量")
    expected_keywords: List[str] = Field(default=[], description="期望出现的关键词，比如['总结','核心']")
    
    class Config:
        use_enum_values = True   # 让枚举值以字符串形式存储


class TaskBatch(BaseModel):
    """一批任务 - 就像一套试卷"""
    batch_id: str = Field(..., description="批次ID")
    name: str = Field(..., description="批次名称，比如'客服问答测试集'")
    description: Optional[str] = Field("", description="批次描述")
    tasks: List[TaskSample] = Field(..., description="任务列表")
    created_at: Optional[str] = Field(None, description="创建时间")


# ==================== 模型配置 ====================
class ModelConfig(BaseModel):
    """模型配置 - 就像菜单上的一道菜"""
    model_config = {"protected_namespaces": ()}  # 解决 Pydantic v2 的 model_ 前缀冲突
    
    model_name: str = Field(..., description="模型名称，比如 'gpt-4o-mini'")
    display_name: Optional[str] = Field(None, description="显示名称")
    provider: str = Field(..., description="服务商：openai / anthropic / openai_compatible")
    model_id: str = Field(..., description="模型ID（调用API时用）")
    api_base: Optional[str] = Field(None, description="API地址（国产模型需要）")
    price_per_1k_input: float = Field(..., description="输入价格，每1000个token多少钱")
    price_per_1k_output: float = Field(..., description="输出价格")
    context_window: int = Field(128000, description="上下文窗口大小")
    speed: str = Field("medium", description="速度：fast / medium / slow")


# ==================== 评估结果数据模型 ====================
class ModelResponse(BaseModel):
    """单个模型的回复结果"""
    model_config = {"protected_namespaces": ()}  # 解决 Pydantic v2 的 model_ 前缀冲突
    
    model_name: str
    task_id: str
    input_tokens: int = 0           # 输入用了多少token
    output_tokens: int = 0           # 输出生成了多少token
    cost: float = 0.0               # 这次调用花了多少钱
    latency: float = 0.0            # 响应时间（秒）
    output_text: str = ""            # 模型生成的回复
    success: bool = True             # 是否成功
    error_message: Optional[str] = None


class QualityScore(BaseModel):
    """质量评分结果"""
    model_config = {"protected_namespaces": ()}  # 解决 Pydantic v2 的 model_ 前缀冲突
    
    model_name: str
    task_id: str
    overall_score: float = 0.0      # 总分（1-10）
    accuracy: float = 0.0            # 准确性（1-10）
    relevance: float = 0.0           # 相关性（1-10）
    completeness: float = 0.0        # 完整性（1-10）
    readability: float = 0.0         # 可读性（1-10）
    reasoning: str = ""               # 评分理由


class TaskEvaluationResult(BaseModel):
    """单个任务的完整评估结果"""
    task_id: str
    task_type: str
    instruction: str
    input_text: str
    reference_output: Optional[str]
    
    # 各个模型的回复
    responses: Dict[str, ModelResponse] = Field(default={})
    # 各个模型的质量评分
    quality_scores: Dict[str, QualityScore] = Field(default={})
    # 综合得分（成本、速度、质量加权）
    comprehensive_scores: Dict[str, float] = Field(default={})


# ==================== 报告数据模型 ====================
class BenchmarkReport(BaseModel):
    """评估报告 - 最终的产出物"""
    report_id: str
    report_title: str = "AI模型选型与投资回报分析报告"
    created_at: str
    
    # 评估配置
    batch_name: str
    models_tested: List[str]
    total_tasks: int
    
    # 评估结果
    task_results: List[TaskEvaluationResult]
    
    # 汇总统计
    summary_stats: Dict[str, Any] = Field(default={})
    
    # 推荐结论
    recommendation: Dict[str, Any] = Field(default={})
    
    # 成本预测（不同调用量下的成本）
    cost_projection: Dict[str, List[Dict]] = Field(default={})


# ==================== 请求/响应模型（给Web API用）====================
class BenchmarkRequest(BaseModel):
    """开始一次评估的请求"""
    model_config = {"protected_namespaces": ()}  # 解决 Pydantic v2 的 model_ 前缀冲突
    
    batch_id: str = Field(..., description="要评估的任务批次ID")
    model_names: List[str] = Field(..., description="要测试的模型列表")
    weights: Dict[str, float] = Field(default={"cost": 0.3, "speed": 0.2, "quality": 0.5}, 
                                      description="评估维度权重")
    judge_model: str = Field(default="gpt-4o-mini", description="评分用的评委模型")


class BenchmarkResponse(BaseModel):
    """评估结果的响应"""
    report_id: str
    status: str  # "running" / "completed" / "failed"
    message: str
    report: Optional[BenchmarkReport] = None

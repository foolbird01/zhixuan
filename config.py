"""
配置文件 - 放所有的配置项
就像餐厅的"设置菜单"，哪些模型可以用、价格是多少，都写在这里
"""

import os
from dotenv import load_dotenv

# 加载 .env 文件里的API Key（这样不用把密钥写死在代码里）
load_dotenv()

# ==================== 支持的模型列表 ====================
# 就像菜单一样，告诉系统"我们能点哪些模型"
# 每个模型有：名字、调用方式、价格（每1000个token多少钱）

AVAILABLE_MODELS = {
    # ==================== 国产模型（推荐，无需翻墙）====================
    # 通义千问 - 阿里云百炼平台
    # 注册：https://dashscope.aliyun.com/ 新用户有100万token免费额度
    "qwen-turbo": {
        "provider": "openai_compatible",
        "model_id": "qwen-turbo",
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "price_per_1k_input": 0.0003,         # 0.002元/千token (约$0.0003)
        "price_per_1k_output": 0.0006,        # 0.006元/千token
        "speed": "fast",
        "context_window": 131072,
        "region": "china",                    # 标记为国内模型
    },
    "qwen-plus": {
        "provider": "openai_compatible",
        "model_id": "qwen-plus",
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "price_per_1k_input": 0.0006,
        "price_per_1k_output": 0.002,
        "speed": "medium",
        "context_window": 131072,
        "region": "china",
    },
    "qwen-max": {
        "provider": "openai_compatible",
        "model_id": "qwen-max",
        "api_base": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "price_per_1k_input": 0.0028,
        "price_per_1k_output": 0.0084,
        "speed": "slow",
        "context_window": 32768,
        "region": "china",
    },
    
    # DeepSeek - 超便宜，推理能力极强
    # 注册：https://platform.deepseek.com/ 充$2能用很久
    "deepseek-chat": {
        "provider": "openai_compatible",
        "model_id": "deepseek-v4-flash",
        "api_base": "https://api.deepseek.com",
        "price_per_1k_input": 0.00014,
        "price_per_1k_output": 0.00028,
        "speed": "fast",
        "context_window": 64000,
        "region": "china",
    },
    "deepseek-reasoner": {
        "provider": "openai_compatible",
        "model_id": "deepseek-v4-pro",
        "api_base": "https://api.deepseek.com",
        "price_per_1k_input": 0.00055,
        "price_per_1k_output": 0.00219,
        "speed": "slow",
        "context_window": 64000,
        "region": "china",
    },
    
    # 智谱GLM - 清华系，性价比高
    # 注册：https://open.bigmodel.cn/ 新用户有免费额度
    "glm-4-flash": {
        "provider": "openai_compatible",
        "model_id": "glm-4-flash",
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
        "price_per_1k_input": 0.00001,        # 超便宜！0.0001元/千token
        "price_per_1k_output": 0.00001,
        "speed": "fast",
        "context_window": 128000,
        "region": "china",
    },
    "glm-4-plus": {
        "provider": "openai_compatible",
        "model_id": "glm-4-plus",
        "api_base": "https://open.bigmodel.cn/api/paas/v4",
        "price_per_1k_input": 0.0007,
        "price_per_1k_output": 0.0007,
        "speed": "medium",
        "context_window": 128000,
        "region": "china",
    },
    
    # 月之暗面 Kimi - 长文本能力强
    # 注册：https://platform.moonshot.cn/ 新用户有免费额度
    "moonshot-v1-8k": {
        "provider": "openai_compatible",
        "model_id": "moonshot-v1-8k",
        "api_base": "https://api.moonshot.cn/v1",
        "price_per_1k_input": 0.000168,
        "price_per_1k_output": 0.000168,
        "speed": "fast",
        "context_window": 8192,
        "region": "china",
    },
    "moonshot-v1-32k": {
        "provider": "openai_compatible",
        "model_id": "moonshot-v1-32k",
        "api_base": "https://api.moonshot.cn/v1",
        "price_per_1k_input": 0.000336,
        "price_per_1k_output": 0.000336,
        "speed": "medium",
        "context_window": 32768,
        "region": "china",
    },
    
    # ==================== 国外模型（需要API Key，可选）====================
    "gpt-4o-mini": {
        "provider": "openai",
        "model_id": "gpt-4o-mini",
        "price_per_1k_input": 0.00015,
        "price_per_1k_output": 0.0006,
        "speed": "fast",
        "context_window": 128000,
        "region": "overseas",
    },
    "gpt-4o": {
        "provider": "openai",
        "model_id": "gpt-4o",
        "price_per_1k_input": 0.0025,
        "price_per_1k_output": 0.01,
        "speed": "medium",
        "context_window": 128000,
        "region": "overseas",
    },
    "claude-3-5-sonnet": {
        "provider": "anthropic",
        "model_id": "claude-3-5-sonnet-20241022",
        "price_per_1k_input": 0.003,
        "price_per_1k_output": 0.015,
        "speed": "medium",
        "context_window": 200000,
        "region": "overseas",
    },
    "claude-3-haiku": {
        "provider": "anthropic",
        "model_id": "claude-3-haiku-20240307",
        "price_per_1k_input": 0.00025,
        "price_per_1k_output": 0.00125,
        "speed": "fast",
        "context_window": 200000,
        "region": "overseas",
    },
}

# ==================== API Key 配置 ====================
# 从环境变量读取（安全！不会泄露密钥）
# 使用方式：在项目根目录创建 .env 文件，写入：
# OPENAI_API_KEY=sk-xxxxxxxxxxxx
# ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxx
# DASHSCOPE_API_KEY=sk-xxxxxxxxxxxx
# DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")   # 阿里云百炼（通义千问）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")     # DeepSeek
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY", "")           # 智谱AI（GLM）
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")     # 月之暗面（Kimi）

# ==================== 评估配置 ====================
# LLM-as-Judge 用来评估质量（用强大的模型当"评委"）
# 默认用国内模型，不需要翻墙！如果你有 OpenAI Key 可以改成 gpt-4o-mini
JUDGE_MODEL = os.getenv("JUDGE_MODEL", "deepseek-v4-pro")       # 评委模型（默认用DeepSeek，便宜又准）
QUALITY_SCORE_THRESHOLDS = {                # 质量评分阈值
    "excellent": 9,                         # 9-10分：优秀
    "good": 7,                              # 7-8分：良好
    "acceptable": 5,                         # 5-6分：及格
    "poor": 0,                              # 0-4分：不及格
}

# ==================== 报告配置 ====================
REPORT_OUTPUT_DIR = "reports"                # 报告保存位置
TEMPLATE_DIR = "templates"                  # 报告模板位置

# ==================== 默认评估维度权重 ====================
# 企业可以根据自己的需求调整这些权重
DEFAULT_WEIGHTS = {
    "cost": 0.3,           # 成本占30%权重
    "speed": 0.2,          # 速度占20%权重
    "quality": 0.5,        # 质量占50%权重（质量最重要）
}

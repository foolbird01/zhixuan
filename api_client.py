"""
API客户端 - 封装所有大模型API调用
就像一个"翻译官"，不管什么模型，都用统一的接口调用
企业只需要说"我要用GPT-4o"，不用管底层怎么调API
"""

import sys
import time
import json
from typing import List, Dict, Any, Optional
import openai

# 修复 Windows GBK 编码问题
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import anthropic
from tenacity import retry, stop_after_attempt, wait_exponential
from config import AVAILABLE_MODELS, OPENAI_API_KEY, ANTHROPIC_API_KEY, DASHSCOPE_API_KEY, DEEPSEEK_API_KEY, ZHIPU_API_KEY, MOONSHOT_API_KEY
from models import ModelResponse, ModelConfig


class ModelAPIClient:
    """
    模型API客户端 - 统一调用接口
    
    为什么需要这个？
    - OpenAI、Anthropic、国产模型的API格式都不一样
    - 这个客户端把它们"统一"成一个接口
    - 就像万能充电器，不管什么手机都能充
    """
    
    def __init__(self):
        """初始化各个服务商的客户端"""
        
        # OpenAI 客户端（也兼容国产模型）
        self.openai_client = openai.OpenAI(
            api_key=OPENAI_API_KEY if OPENAI_API_KEY else "dummy",
        ) if OPENAI_API_KEY else None
        
        # Anthropic 客户端
        self.anthropic_client = anthropic.Anthropic(
            api_key=ANTHROPIC_API_KEY if ANTHROPIC_API_KEY else "dummy",
        ) if ANTHROPIC_API_KEY else None
        
        print("API客户端初始化完成")
        print(f"   通义千问(阿里云): {'已配置' if DASHSCOPE_API_KEY else '未配置'}")
        print(f"   DeepSeek: {'已配置' if DEEPSEEK_API_KEY else '未配置'}")
        print(f"   智谱GLM: {'已配置' if ZHIPU_API_KEY else '未配置'}")
        print(f"   Kimi(月之暗面): {'已配置' if MOONSHOT_API_KEY else '未配置'}")
        print(f"   OpenAI: {'已配置' if OPENAI_API_KEY else '未配置(可选)'}")
        print(f"   Anthropic: {'已配置' if ANTHROPIC_API_KEY else '未配置(可选)'}")
    
    
    def _get_api_key_for_model(self, provider: str) -> str:
        """根据服务商返回对应的API Key"""
        key_map = {
            "openai": OPENAI_API_KEY,
            "anthropic": ANTHROPIC_API_KEY,
            "openai_compatible": {  # 国产模型用 openai_compatible
                "qwen-turbo": DASHSCOPE_API_KEY,
                "qwen-plus": DASHSCOPE_API_KEY,
                "deepseek-chat": DEEPSEEK_API_KEY,
            }
        }
        
        if provider == "openai_compatible":
            # 这个逻辑在 _call_openai_compatible 里处理
            return ""
        return key_map.get(provider, "")
    
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=60))
    def call_model(
        self,
        model_config: ModelConfig,
        instruction: str,
        input_text: str = "",
        max_tokens: int = 1000,
    ) -> ModelResponse:
        """
        统一调用接口 - 不管什么模型，都用这个方法
        
        参数：
        - model_config: 模型配置（从config.py读取）
        - instruction: 任务指令（比如"总结下面这段话"）
        - input_text: 输入文本（比如要总结的那段话）
        - max_tokens: 最多生成多少token
        
        返回：
        - ModelResponse 对象（包含回复、耗时、花费等）
        
        为什么要用 @retry？
        - API偶尔会失败（网络抖动、限流等）
        - 自动重试3次，提高成功率
        """
        
        # 拼接完整提示词
        if input_text:
            full_prompt = f"{instruction}\n\n{input_text}"
        else:
            full_prompt = instruction
        
        start_time = time.time()
        
        try:
            # 根据服务商选择不同的调用方式
            if model_config.provider == "openai":
                return self._call_openai(model_config, full_prompt, max_tokens, start_time)
            
            elif model_config.provider == "anthropic":
                return self._call_anthropic(model_config, full_prompt, max_tokens, start_time)
            
            elif model_config.provider == "openai_compatible":
                return self._call_openai_compatible(model_config, full_prompt, max_tokens, start_time)
            
            else:
                raise ValueError(f"不支持的服务商: {model_config.provider}")
        
        except Exception as e:
            # 如果失败了，返回一个失败的响应
            elapsed = time.time() - start_time
            return ModelResponse(
                model_name=model_config.model_name,
                task_id="",
                latency=elapsed,
                output_text="",
                success=False,
                error_message=str(e),
            )
    
    
    def _call_openai(
        self,
        model_config: ModelConfig,
        prompt: str,
        max_tokens: int,
        start_time: float,
    ) -> ModelResponse:
        """调用 OpenAI API（GPT-4o、GPT-4o-mini 等）"""
        
        if not self.openai_client:
            raise ValueError("OpenAI API Key 未配置")
        
        # 调用 Chat Completions API
        response = self.openai_client.chat.completions.create(
            model=model_config.model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,   # 控制创造性，0.7是比较平衡的值
        )
        
        elapsed = time.time() - start_time
        
        # 提取回复内容
        output_text = response.choices[0].message.content
        
        # 计算花费
        input_tokens = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens
        cost = (input_tokens / 1000 * model_config.price_per_1k_input +
                output_tokens / 1000 * model_config.price_per_1k_output)
        
        return ModelResponse(
            model_name=model_config.model_name,
            task_id="",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency=elapsed,
            output_text=output_text,
            success=True,
        )
    
    
    def _call_anthropic(
        self,
        model_config: ModelConfig,
        prompt: str,
        max_tokens: int,
        start_time: float,
    ) -> ModelResponse:
        """调用 Anthropic API（Claude 系列）"""
        
        if not self.anthropic_client:
            raise ValueError("Anthropic API Key 未配置")
        
        # Claude 的 API 格式跟 OpenAI 不一样
        response = self.anthropic_client.messages.create(
            model=model_config.model_id,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        
        elapsed = time.time() - start_time
        
        # Claude 的回复格式不一样
        output_text = response.content[0].text
        
        # 计算花费（Claude 的 token 计数方式）
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        cost = (input_tokens / 1000 * model_config.price_per_1k_input +
                output_tokens / 1000 * model_config.price_per_1k_output)
        
        return ModelResponse(
            model_name=model_config.model_name,
            task_id="",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency=elapsed,
            output_text=output_text,
            success=True,
        )
    
    
    def _call_openai_compatible(
        self,
        model_config: ModelConfig,
        prompt: str,
        max_tokens: int,
        start_time: float,
    ) -> ModelResponse:
        """
        调用兼容 OpenAI 格式的 API（国产模型）
        
        为什么叫 "openai_compatible"？
        - 阿里云百炼、DeepSeek 等国产模型
        - 为了吸引开发者，API 格式故意做得跟 OpenAI 一模一样
        - 所以可以用 OpenAI 的客户端来调用，只需要改个 base_url
        """
        
        # 根据模型名称找到对应的 API Key
        if "qwen" in model_config.model_name:
            api_key = DASHSCOPE_API_KEY
        elif "deepseek" in model_config.model_name:
            api_key = DEEPSEEK_API_KEY
        elif "glm" in model_config.model_name:
            api_key = ZHIPU_API_KEY
        elif "moonshot" in model_config.model_name:
            api_key = MOONSHOT_API_KEY
        else:
            raise ValueError(f"未知的国产模型: {model_config.model_name}")
        
        if not api_key:
            raise ValueError(f"{model_config.model_name} 的 API Key 未配置")
        
        # 创建一个临时的 OpenAI 客户端，但 base_url 指向国产厂商
        client = openai.OpenAI(
            api_key=api_key,
            base_url=model_config.api_base,   # 关键！指向国产厂商的API地址
        )
        
        response = client.chat.completions.create(
            model=model_config.model_id,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        
        elapsed = time.time() - start_time
        
        output_text = response.choices[0].message.content
        
        # 国产模型有的不返回 token 用量，需要手动计算
        input_tokens = response.usage.prompt_tokens if response.usage else 0
        output_tokens = response.usage.completion_tokens if response.usage else 0
        
        # 如果没返回 token 用量，用 tiktoken 估算（这里简化，设为0）
        if input_tokens == 0:
            # 简单估算：1个中文字≈2个token，1个英文词≈1.3个token
            input_tokens = len(prompt) // 2
            output_tokens = len(output_text) // 2
        
        cost = (input_tokens / 1000 * model_config.price_per_1k_input +
                output_tokens / 1000 * model_config.price_per_1k_output)
        
        return ModelResponse(
            model_name=model_config.model_name,
            task_id="",
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cost=cost,
            latency=elapsed,
            output_text=output_text,
            success=True,
        )
    
    
    def count_tokens(self, text: str, model_name: str = "gpt-4o-mini") -> int:
        """
        计算文本的 token 数
        
        为什么要算 token？
        - API 按 token 收费，知道用了多少 token 就知道花了多少钱
        - 大模型有上下文限制（比如 128000 tokens），超了会报错
        
        为什么不同模型 token 数不一样？
        - 英文：1个词≈1.3个token
        - 中文：1个字≈2个token（因为中文字符多）
        """
        try:
            import tiktoken
            # 用 tiktoken 精确计算（OpenAI 开源的工具）
            enc = tiktoken.encoding_for_model("gpt-4o")  # 用 gpt-4o 的编码器
            return len(enc.encode(text))
        except:
            # 如果 tiktoken 不可用，用简单估算
            # 中文按字符数，英文按单词数
            chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
            english_words = len(text.split())
            return chinese_chars * 2 + english_words

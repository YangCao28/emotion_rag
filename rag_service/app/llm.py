import os
import logging
from openai import OpenAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 初始化 OpenAI 客户端，使用阿里云百炼兼容模式
# 这个客户端实例被 prompt_builder.py 共享使用
def get_llm_client():
    """
    获取配置好的 LLM 客户端实例
    
    Returns:
        OpenAI: 配置好的客户端实例
    """
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error("DASHSCOPE_API_KEY not set")
        raise ValueError("DASHSCOPE_API_KEY environment variable is required")
    
    return OpenAI(
        api_key=api_key,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    )

# 全局客户端实例，供其他模块使用
try:
    client = get_llm_client()
    logger.info("LLM client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize LLM client: {e}")
    client = None

# 模型配置常量
LLM_MODEL = "qwen-vl-max-latest"
DEFAULT_TEMPERATURE = 0.4
DEFAULT_TOP_P = 0.8
DEFAULT_MAX_TOKENS = 1024

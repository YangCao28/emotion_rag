import os
import logging
from typing import Dict, Any, List, Optional
from uuid import uuid4
from app.llm import client, LLM_MODEL, DEFAULT_TEMPERATURE, DEFAULT_TOP_P, DEFAULT_MAX_TOKENS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_background():
    bg_env = os.getenv("BACKGROUND", "").strip()
    if not bg_env:
        logger.warning("No BACKGROUND environment variable set, using empty background.")
        return ""
    if os.path.isfile(bg_env):
        logger.info(f"Loading background from file: {bg_env}")
        try:
            with open(bg_env, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Failed to read background file '{bg_env}': {e}")
            return ""
    logger.info("Using BACKGROUND as raw string.")
    return bg_env

BACKGROUND = load_background()

def query_llm_with_prompt(user_input, emotion, retrieved_docs, attachments=None, background=BACKGROUND):
    """
    构建 prompt 并调用 Qwen API（集成版本）
    
    Args:
        user_input: 用户输入文本
        emotion: 情感状态
        retrieved_docs: 检索到的相关文档
        attachments: 附件列表（可能包含多个图像URL）
        background: 角色背景
        
    Returns:
        模型响应结果
    """
    logger.info(f"Processing request for user input: {user_input[:50]}...")
    
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        logger.error("DASHSCOPE_API_KEY not set")
        return {
            "content": "API Key 未配置，请联系管理员。",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "id": str(uuid4())
        }
    
    try:
        # 构建系统消息
        if emotion is None:
            emotion = "平静"
        
        system_content = (
            f"你是夏鸣星，是用户的恋人。夏鸣星背景 {background}\n"
            "请用温柔、真实的语气回应她。\n"
            "不要重复她说的话，不要总结，不要分析，只表达你真实的回应。\n"
            "只能参考资料，不允许编造，不要描述对方的任何具体生理外貌特征。\n"
            "如果用户提供了图片，请观察图片内容并给出相应的回应。"
        )
        
        # 构建用户消息内容
        doc_text = "\n".join(retrieved_docs)
        user_text_content = f"【用户输入】：{user_input}\n【你可以参考的资料】：{doc_text}"
        
        # 处理图像附件（支持多个图像URL）
        image_urls = []
        non_image_attachments = []
        
        if attachments:
            for attachment in attachments:
                if attachment.get("type", "").startswith("image/"):
                    image_urls.append(attachment.get("url", ""))
                else:
                    non_image_attachments.append(attachment)
            
            # 记录附件处理信息
            if image_urls:
                logger.info(f"Found {len(image_urls)} image URLs: {[url[:50] + '...' for url in image_urls]}")
            
            if non_image_attachments:
                logger.info(f"Ignoring {len(non_image_attachments)} non-image attachments")
        
        # 构建 OpenAI 兼容格式的消息
        openai_messages = [
            {
                "role": "system",
                "content": system_content
            }
        ]
        
        # 根据是否有图像决定用户消息格式
        if image_urls:
            # 多模态格式：文本 + 多个图像
            user_content = [
                {
                    "type": "text",
                    "text": user_text_content
                }
            ]
            
            # 添加所有图像URL
            for url in image_urls:
                user_content.append({
                    "type": "image_url",
                    "image_url": {
                        "url": url
                    }
                })
            
            openai_messages.append({
                "role": "user",
                "content": user_content
            })
        else:
            # 纯文本格式
            openai_messages.append({
                "role": "user",
                "content": user_text_content
            })
        
        logger.info(f"Sending request to Qwen API with {len(image_urls)} images")
        
        # 调用 API，使用配置常量
        completion = client.chat.completions.create(
            model=LLM_MODEL,
            messages=openai_messages,
            temperature=DEFAULT_TEMPERATURE,
            top_p=DEFAULT_TOP_P,
            max_tokens=DEFAULT_MAX_TOKENS
        )
        
        # 提取响应内容和token统计
        content = completion.choices[0].message.content
        usage = completion.usage
        
        logger.info(f"Received response from Qwen API: {completion.id}")
        logger.info(f"Token usage - Prompt: {usage.prompt_tokens}, Completion: {usage.completion_tokens}, Total: {usage.total_tokens}")
        
        return {
            "content": content,
            "usage": {
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            },
            "id": completion.id,
            "image_count": len(image_urls),
            "doc_count": len(retrieved_docs)
        }
        
    except Exception as e:
        logger.error(f"Error calling Qwen API: {e}")
        return {
            "content": "处理请求时发生错误，请稍后重试。",
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
            "id": str(uuid4()),
            "image_count": 0,
            "doc_count": len(retrieved_docs) if retrieved_docs else 0
        }

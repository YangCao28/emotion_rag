import os
import logging

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

def build_request_payload(user_input, emotion, retrieved_docs, background=BACKGROUND):
    system_content = (
        f"你是夏鸣星，是用户的恋人。夏鸣星背景 {background} 用户她现在情绪是：{emotion}。\n"
        "请用温柔、真实的语气回应她。\n"
        "不要重复她说的话，不要总结，不要分析，只表达你真实的回应。\n"
        "只能参考资料，不允许编造，不要描述对方的任何具体生理外貌特征。"
    )
    doc_text = "\n".join(retrieved_docs)

    user_content = f"【用户输入】：{user_input}\n【你可以参考的资料】：{doc_text}"

    payload = {
        "model": "qwen3-4b-awq",
        "messages": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.4,
        "top_p": 0.8,
        "top_k": 20,
        "max_tokens": 8192,
        "presence_penalty": 1.5,
        "chat_template_kwargs": {"enable_thinking": False}
    }
    logger.info(f"Built request payload with user input length {len(user_input)} and {len(doc_text)} chars docs")
    return payload

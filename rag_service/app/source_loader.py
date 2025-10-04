import os
import re
def get_character_quotes_path():
    # 先尝试从环境变量读取
    env_path = os.getenv("CHARACTER_QUOTES_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path
    
    # 环境变量没设置或文件不存在，使用默认相对路径
    default_path = os.path.join(os.path.dirname(__file__), "..", "data", "character_quotes.txt")
    return default_path
CHARACTER_QUOTES_PATH = get_character_quotes_path()
def load_documents():
    with open(CHARACTER_QUOTES_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    # 用正则按空行分割文本成多个段落
    paragraphs = [p.strip() for p in re.split(r'\n\s*\n', text) if p.strip()]

    return paragraphs

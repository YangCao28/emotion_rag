import logging
from snownlp import SnowNLP

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_sentiment(text: str) -> str:
    logger.info(f"Analyzing sentiment for text of length {len(text)}")
    score = SnowNLP(text).sentiments
    if score > 0.75:
        emotion = "愉快"
    elif score > 0.55:
        emotion = "平静"
    elif score > 0.35:
        emotion = "焦虑"
    elif score > 0.15:
        emotion = "悲伤"
    else:
        emotion = "愤怒"
    logger.info(f"Sentiment score: {score}, classified as {emotion}")
    return emotion

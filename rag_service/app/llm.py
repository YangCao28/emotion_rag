import os
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://localhost:8000")

def query_llm(payload):
    logger.info(f"Sending prompt to model service at {MODEL_SERVICE_URL} with length {len(payload)}")
    try:
        response = requests.post(f"{MODEL_SERVICE_URL}/v1/chat/completions", json=payload)
        response.raise_for_status()
        resp = response.json()
        completion_id = resp.get("id", "")
        usage = resp.get("usage", {}) 
        choices = resp.get("choices", [])
        if choices and len(choices) > 0:
            content = choices[0].get("message", {}).get("content", "")
        else:
            content = ""
        logger.info(f"Received response from model service with length {len(content)}")
        return {"content": content, "usage": usage,"completion_id": completion_id}

    except Exception as e:
        logger.error(f"Error querying model service: {e}")
        return {}

import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.embedder import EmbeddingModel
from app.chroma_client import ChromaDB
from app.emotion import get_sentiment
from app.prompt_builder import build_request_payload
from app.llm import query_llm
from app.config import MODEL_SERVICE_URL
from app.build_index import build_rag_DB

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

embedder = EmbeddingModel()
db = build_rag_DB()

class QueryRequest(BaseModel):
    message_id: str
    text: str

@app.post("/generate")
def generate(req: QueryRequest):
    user_text = req.text
    message_id = req.message_id

    logger.info(f"Request message_id={message_id}, user_text={user_text[:50]}...")

    try:
        emotion = get_sentiment(user_text)
        logger.info(f"Emotion detected: {emotion}")

        embedding = embedder.encode([user_text])[0]
        logger.info(f"Embedding vector length: {len(embedding)}")

        docs = db.query(embedding, top_k=4)
        logger.info(f"Retrieved {len(docs)} RAG docs.")

        payload = build_request_payload(user_text, emotion, docs)
        logger.info(f"Payload prepared for LLM, length approx: {len(str(payload))}")

        resp = query_llm(payload)
        content = resp.get("content", "")
        usage = resp.get("usage", {})
        completion_id = resp.get("id")
        if not completion_id:
            import uuid
            completion_id = str(uuid.uuid4())  # 生成唯一ID代替

        logger.info(f"Received completion_id={completion_id} with response length={len(content)}")

        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        total_tokens = usage.get("total_tokens", 0)

        return {
            "message_id": message_id,
            "response_text": content,
            "user_text":user_text,
            "emotion":emotion,
            "rag_docs":docs,
            "completion_id":completion_id,
            "completion_tokens":completion_tokens,
            "total_tokens":total_tokens,
            "prompt_tokens":prompt_tokens
        }

    except Exception as e:
        logger.error(f"Error in /generate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

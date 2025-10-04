import os
import logging
from typing import List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 本地模块
from app.source_loader import load_documents
from app.prompt_builder import query_llm_with_prompt

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ----------- 初始化 embedding 实例 -----------
embeddings = HuggingFaceEmbeddings(model_name="Qwen/Qwen3-Embedding-0.6B")

# ----------- 构建向量库函数 -----------

def build_rag_DB() -> Optional[Chroma]:
    raw_docs: List[str] = load_documents()
    logger.info(f"Loaded {len(raw_docs)} raw docs")

    texts = [d.strip() for d in raw_docs if d.strip()]
    if not texts:
        logger.warning("No valid documents loaded, skipping build")
        return None

    splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    documents = splitter.split_documents([Document(page_content=d) for d in texts])
    logger.info(f"Split into {len(documents)} chunks")

    vectordb = Chroma(
        collection_name="emotion-collection",
        embedding_function=embeddings,
        persist_directory="./chroma_data",
    )
    uuids = [str(uuid4()) for _ in range(len(documents))]
    vectordb.add_documents(documents=documents, ids=uuids)

    count = vectordb._collection.count() if vectordb._collection else len(documents)
    logger.info(f"Inserted {count} documents into Chroma")
    return vectordb

# ----------- 加载或重建向量库 -----------

def load_or_build_db() -> Optional[Chroma]:
    if os.path.exists("./chroma_data") and os.listdir("./chroma_data"):
        logger.info("Loading existing Chroma DB from disk...")
        db = Chroma(
            collection_name="emotion-collection",
            embedding_function=embeddings,
            persist_directory="./chroma_data"
        )
        count = db._collection.count() if db._collection else 0
        logger.info(f"Loaded Chroma DB with {count} vectors")
        if count == 0:
            logger.warning("Warning: Chroma DB is empty!")
        return db
    else:
        logger.info("Chroma DB not found or empty, building new DB")
        return build_rag_DB()

db = load_or_build_db()
if db is None:
    logger.error("Failed to load or build Chroma DB")
    raise RuntimeError("Vector DB initialization failed")

# ----------- FastAPI 服务和请求处理 -----------

app = FastAPI()

class Attachment(BaseModel):
    url: str
    filename: str
    type: str
    size: int

class QueryRequest(BaseModel):
    message_id: str
    text: str
    attachments: Optional[List[Attachment]] = None
    has_attachments: bool = False

@app.post("/generate")
def generate(req: QueryRequest):
    user_text = req.text
    message_id = req.message_id
    attachments = req.attachments or []
    has_attachments = req.has_attachments

    logger.info(f"Request message_id={message_id}, user_text={user_text[:50]}...")
    
    # 处理附件信息（仅用于日志记录，不参与向量搜索）
    if has_attachments and attachments:
        logger.info(f"Processing {len(attachments)} attachments")
        attachment_details = []
        for att in attachments:
            attachment_details.append(f"文件名: {att.filename}, 类型: {att.type}, 大小: {att.size} bytes")
        attachment_info = f"用户上传了 {len(attachments)} 个附件：\n" + "\n".join(attachment_details)
        logger.info(f"Attachment info: {attachment_info}")

    try:
        # 使用原始用户文本进行向量搜索（不包含附件信息）
        logger.info(f"Performing vector search with user text only: '{user_text[:50]}...'")
        user_emb = embeddings.embed_query(user_text)
        docs = db.similarity_search_by_vector(user_emb, k=4)
        rag_texts = [doc.page_content for doc in docs]

        # 构建附件字典列表，用于传递给 prompt_builder
        attachment_dicts = [att.dict() for att in attachments] if attachments else None
        
        # 使用合并的函数：构建prompt并调用LLM
        resp = query_llm_with_prompt(
            user_input=user_text,
            emotion=None, 
            retrieved_docs=rag_texts,
            attachments=attachment_dicts
        )
        
        content = resp.get("content", "")
        usage = resp.get("usage", {})
        completion_id = resp.get("id") or str(uuid4())
        image_count = resp.get("image_count", 0)
        doc_count = resp.get("doc_count", 0)

        logger.info(f"Completion id={completion_id}, response length={len(content)}")
        logger.info(f"Processed {image_count} images and {doc_count} documents")

        return {
            "message_id": message_id,
            "response_text": content,
            "user_text": user_text,
            "emotion": None,
            "rag_docs": rag_texts,
            "completion_id": completion_id,
            "completion_tokens": usage.get("completion_tokens", 0),
            "total_tokens": usage.get("total_tokens", 0),
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "attachments": [att.dict() for att in attachments] if attachments else [],
            "has_attachments": has_attachments,
            "attachment_count": len(attachments) if attachments else 0
        }
    except Exception as e:
        logger.error(f"Error in /generate: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

import os
import logging
from app.embedder import EmbeddingModel
from app.chroma_client import ChromaDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_data(file_path):
    logger.info(f"Reading data from {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def build_rag_DB():
    file_path = os.getenv("CHARACTER_QUOTES_PATH", "data/character_quotes.txt")
    texts = read_data(file_path)

    embedder = EmbeddingModel()
    embeddings = embedder.encode(texts)

    db = ChromaDB()
    db.add_documents(texts, embeddings)
    logger.info(f"Vector database built successfully with {len(texts)} entries.")
    return db

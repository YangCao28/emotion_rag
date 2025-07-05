import os
import logging
import uuid
import chromadb
from chromadb.config import Settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChromaDB:
    def __init__(self):
        persist_path = os.getenv("CHROMA_PERSIST_PATH", "chroma_store")
        logger.info(f"Initializing ChromaDB with path: {persist_path}")
        
        self.client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory=persist_path
        ))

        self.collection = self.client.get_or_create_collection(name="persona")
        logger.info("ChromaDB collection 'persona' initialized.")

    def add_documents(self, texts, embeddings):
        if not texts or not embeddings.any():
            logger.warning("Empty texts or embeddings received, skipping add.")
            return
        
        logger.info(f"Adding {len(texts)} documents to ChromaDB...")
        ids = [str(uuid.uuid4()) for _ in range(len(texts))]

        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings.tolist(),
                ids=ids
            )
            logger.info("Documents added successfully.")
        except Exception as e:
            logger.error(f"Failed to add documents to ChromaDB: {e}")

    def query(self, embedding, top_k=3):
        logger.info(f"Querying top {top_k} documents from ChromaDB...")
        try:
            results = self.collection.query(
                query_embeddings=[embedding.tolist()],
                n_results=top_k
            )
            docs = results.get("documents", [[]])[0]
            logger.info(f"Query returned {len(docs)} documents.")
            return docs
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return []

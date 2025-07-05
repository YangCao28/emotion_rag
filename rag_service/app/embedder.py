import logging
from transformers import AutoTokenizer, AutoModel
import torch

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmbeddingModel:
    def __init__(self, model_name='BAAI/bge-small-zh'):
        logger.info(f"Loading embedding model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        logger.info("Embedding model loaded successfully.")

    def encode(self, texts):
        logger.info(f"Encoding {len(texts)} texts...")
        inputs = self.tokenizer(texts, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0]
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings.cpu().numpy()

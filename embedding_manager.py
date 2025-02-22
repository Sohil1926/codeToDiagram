import os
import logging
import numpy as np
from abc import ABC, abstractmethod
from typing import List
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt

logger = logging.getLogger(__name__)

class BaseEmbedder(ABC):
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        pass

class OpenAIEmbedder(BaseEmbedder):
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "text-embedding-3-small"
        self.dimensions = 1536  # Can reduce to 512 for cost savings
        self.batch_size = 2048  # Max tokens per batch

    @retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(3))
    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        try:
            response = self.client.embeddings.create(
                input=texts,
                model=self.model,
                dimensions=self.dimensions
            )
            return [np.array(embedding.embedding) for embedding in response.data]
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise

# class HuggingFaceEmbedder(BaseEmbedder):  # Example alternative
#     def __init__(self, model_name="sentence-transformers/all-mpnet-base-v2"):
#         from sentence_transformers import SentenceTransformer
#         self.model = SentenceTransformer(model_name)
        
#     def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
#         return self.model.encode(texts, convert_to_numpy=True)

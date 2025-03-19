import os
import logging
import numpy as np
from abc import ABC, abstractmethod
from typing import List
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
import tiktoken
import time

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
        self.batch_size = 16  # Much smaller batch size to avoid rate limits
        self.token_limit = 8191  # Max tokens per input for this model
        # Initialize tiktoken encoder for token counting
        try:
            self.encoder = tiktoken.encoding_for_model(self.model)
        except:
            self.encoder = tiktoken.get_encoding("cl100k_base")  # Fallback encoding

    def _count_tokens(self, text: str) -> int:
        """Count tokens in a single text using tiktoken."""
        return len(self.encoder.encode(text))

    def _chunk_text(self, text: str, chunk_size: int = 4000, overlap: int = 200) -> List[str]:
        """Chunk text into smaller pieces with overlap."""
        tokens = self.encoder.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), chunk_size - overlap):
            chunk = tokens[i:i + chunk_size]
            chunks.append(self.encoder.decode(chunk))
            
        return chunks

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
    def embed_texts(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for a list of texts.
        
        This method handles:
        - Chunking texts that exceed the token limit
        - Processing in small batches to avoid rate limits
        - Combining chunk embeddings for long texts
        """
        result_embeddings = []
        
        # Process each text individually
        for i, text in enumerate(texts):
            token_count = self._count_tokens(text)
            
            # Log progress for larger batches
            if len(texts) > 10 and i % 10 == 0:
                logger.info(f"Processing text {i} of {len(texts)}")
            
            # For long texts that exceed the token limit
            if token_count > self.token_limit:
                logger.info(f"Text {i} exceeds token limit ({token_count} > {self.token_limit}). Chunking...")
                chunks = self._chunk_text(text)
                chunk_embeddings = []
                
                # Process chunks in small batches
                for j in range(0, len(chunks), self.batch_size):
                    batch = chunks[j:j + self.batch_size]
                    try:
                        response = self.client.embeddings.create(
                            input=batch,
                            model=self.model,
                            dimensions=self.dimensions
                        )
                        batch_embeddings = [np.array(data.embedding) for data in response.data]
                        chunk_embeddings.extend(batch_embeddings)
                        
                        # Add a small delay to avoid rate limits
                        time.sleep(0.2)
                    except Exception as e:
                        logger.error(f"OpenAI API error on chunk batch for text {i}: {str(e)}")
                        raise
                
                # Average the chunk embeddings to get a single embedding for the original text
                if chunk_embeddings:
                    avg_embedding = np.mean(chunk_embeddings, axis=0)
                    result_embeddings.append(avg_embedding)
                else:
                    logger.error(f"No embeddings generated for text {i}")
                    result_embeddings.append(np.zeros(self.dimensions))
            else:
                # For texts within the token limit, process directly
                try:
                    response = self.client.embeddings.create(
                        input=[text],
                        model=self.model,
                        dimensions=self.dimensions
                    )
                    embedding = np.array(response.data[0].embedding)
                    result_embeddings.append(embedding)
                    
                    # Add a small delay to avoid rate limits
                    time.sleep(0.1)
                except Exception as e:
                    logger.error(f"OpenAI API error on text {i}: {str(e)}")
                    raise
        
        return result_embeddings

import os
import logging
from typing import List, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.models import PointStruct
from processed_document import ProcessedDocument
import uuid
import psycopg2
from psycopg2.extras import execute_batch

logger = logging.getLogger(__name__)

class ProcessedDocumentDAO:
    #embedder is optional, because document will already have embeddings
    def __init__(self, embedder: Optional[object] = None):
        """
        Initialize Qdrant client with optional embedder
        :param embedder: Object with embed_texts() method
        """
        self.embedder = embedder
        # Initialize both Qdrant and Postgres connections
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL", "http://localhost:6333"),
            #api key needed during production environment
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.pg_conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            host=os.getenv("POSTGRES_HOST", "localhost")
        )
        self.collection_name = "code_embeddings"
        self._initialize_collection()

    def _initialize_collection(self):
        """Create collection if it doesn't exist"""
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI text-embedding-3-small dimension
                    distance=models.Distance.COSINE
                )
            )

    def batch_save(self, documents: List[ProcessedDocument]):
        """Store documents in both Qdrant and PostgreSQL"""
        try:
            # Generate embeddings if not present
            if self.embedder and any(doc.embedding is None for doc in documents):
                texts = [doc.content for doc in documents]
                embeddings = self.embedder.embed_texts(texts)
                for doc, emb in zip(documents, embeddings):
                    doc.embedding = emb

            # Save to PostgreSQL
            with self.pg_conn.cursor() as cur:
                execute_batch(cur, """
                    INSERT INTO processed_documents 
                    (content, file_name, file_size, timestamp, original_file, embedding)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, [
                    (
                        doc.content,
                        doc.file_name,
                        doc.file_size,
                        doc.timestamp,
                        doc.original_file,
                        doc.embedding.tolist() if doc.embedding is not None else None
                    )
                    for doc in documents
                ])
            self.pg_conn.commit()
            logger.info(f"Inserted {len(documents)} documents into PostgreSQL")

            # Save to Qdrant (keeping vector search capability)
            points = [
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=doc.embedding.tolist(),
                    payload={
                        "content": doc.content,
                        "file_name": doc.file_name,
                        "original_file": doc.original_file
                    }
                ) for doc in documents if doc.embedding is not None
            ]
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            logger.info(f"Inserted {len(points)} documents into Qdrant")
            
        except Exception as e:
            logger.error(f"Batch save failed: {str(e)}")
            raise

    def search(self, query: str, top_k: int = 5, **filters) -> List[ProcessedDocument]:
        """Search similar documents with optional filters"""
        try:
            # Generate query embedding
            query_embedding = self.embedder.embed_texts([query])[0]
            
            # Build Qdrant filter
            qdrant_filter = self._build_filter(filters) if filters else None
            
            # Execute search
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                query_filter=qdrant_filter,
                limit=top_k
            )
            
            return self._convert_to_processed_docs(results)
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return []

    def _build_filter(self, filter_dict: dict) -> models.Filter:
        """Convert filter dict to Qdrant Filter"""
        return models.Filter(
            must=[
                models.FieldCondition(
                    key=key,
                    match=models.MatchValue(value=value)
                ) for key, value in filter_dict.items()
            ]
        )

    def _convert_to_processed_docs(self, results) -> List[ProcessedDocument]:
        """Convert Qdrant results to ProcessedDocument objects"""
        return [
            ProcessedDocument(
                content=hit.payload["content"],
                file_name=hit.payload["file_name"],
                file_size=len(hit.payload["content"]),
                timestamp="",  # Qdrant doesn't store timestamps
                original_file=hit.payload["original_file"],
                embedding=np.array(hit.vector)
            ) for hit in results
        ]

    def get_all_documents(self, batch_size: int = 100) -> List[ProcessedDocument]:
        """Fetch all documents from the collection using pagination"""
        try:
            all_documents = []
            offset = None
            
            while True:
                results = self.client.scroll(
                    collection_name=self.collection_name,
                    limit=batch_size,
                    offset=offset
                )
                
                # Break if no more results
                if not results[0]:
                    break
                    
                # Convert to ProcessedDocument objects
                documents = self._convert_to_processed_docs(results[0])
                all_documents.extend(documents)
                
                # Update offset for next batch
                offset = results[1]
                
                if offset is None:  # No more records
                    break
                    
            logger.info(f"Retrieved {len(all_documents)} documents")
            return all_documents
            
        except Exception as e:
            logger.error(f"Failed to fetch all documents: {str(e)}")
            return []

    def delete_all_documents(self) -> bool:
        """Delete all documents from the collection"""
        try:
            # Recreate the collection (faster than deleting all points)
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI text-embedding-3-small dimension
                    distance=models.Distance.COSINE
                )
            )
            logger.info("All documents deleted successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete all documents: {str(e)}")
            return False

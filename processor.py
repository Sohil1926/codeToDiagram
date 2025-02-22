from abc import ABC, abstractmethod
from typing import List, Optional
from processed_document import ProcessedDocument
from raw_document import RawDocument
from datetime import datetime
from embedding_manager import OpenAIEmbedder
from processed_document_dao import ProcessedDocumentDAO

class BaseProcessor(ABC):
    """
    Base class for all processors.
    Each source-specific processor will inherit from this.
    """
    def __init__(self):
        pass

    @abstractmethod
    def process(self, raw_documents: List[RawDocument], save_to_db: bool = True) -> List[ProcessedDocument]:
        """Each source-specific processor will implement this method"""
        pass

class GitHubProcessor(BaseProcessor):
    def __init__(self, embedder=None):
        # Initialize with any embedder that has embed_texts() method
        self.embedder = embedder or OpenAIEmbedder()
        self.processed_document_dao = ProcessedDocumentDAO(embedder=self.embedder)

    def process(self, raw_documents: List[RawDocument], save_to_db: bool = True) -> List[ProcessedDocument]:
        # Convert raw to processed docs (1:1 mapping)
        processed_docs = [
            ProcessedDocument(
                content=raw_doc.content,
                file_name=raw_doc.file_name,
                file_size=raw_doc.file_size,
                timestamp=raw_doc.timestamp,
                original_file=raw_doc.original_file,
                chunk_metadata=raw_doc.chunk_metadata,
                embedding=None
            ) for raw_doc in raw_documents
        ]

        # Generate embeddings for all documents
        texts = [doc.content for doc in processed_docs]
        embeddings = self.embedder.embed_texts(texts)
        
        # Assign embeddings to processed documents
        for doc, embedding in zip(processed_docs, embeddings):
            doc.embedding = embedding
        
        if save_to_db:
            self.processed_document_dao.batch_save(processed_docs)
            
        return processed_docs
import os
from sqlalchemy import create_engine, Column, Integer, String, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List
from datetime import datetime

from raw_document import RawDocument

Base = declarative_base()

class RawDocumentDAO(Base):
    __tablename__ = 'raw_documents'
    
    id = Column(Integer, primary_key=True)
    content = Column(String)
    file_name = Column(String)
    file_size = Column(Integer)
    timestamp = Column(DateTime)
    original_file = Column(String)
    chunk_metadata = Column(JSON)

    @classmethod
    def batch_save(cls, documents: List[RawDocument]) -> None:
        """Batch save RawDocuments to the database"""
        db = SessionLocal()
        try:
            # Convert RawDocuments to RawDocumentDAOs
            dao_objects = [
                cls(
                    content=doc.content,
                    file_name=doc.file_name,
                    file_size=doc.file_size,
                    timestamp=datetime.fromisoformat(doc.timestamp),
                    original_file=doc.original_file,
                    chunk_metadata=doc.chunk_metadata
                )
                for doc in documents
            ]
            
            # Bulk save
            db.bulk_save_objects(dao_objects)
            db.commit()
        finally:
            db.close()

    @classmethod
    def get_documents_by_timestamp(cls, start_time: str = None, end_time: str = None) -> List[RawDocument]:
        """Fetch RawDocuments from the database within a timestamp range"""
        db = SessionLocal()
        try:
            # Build query
            query = db.query(cls)
            
            # Add timestamp filters if provided
            if start_time:
                query = query.filter(cls.timestamp >= datetime.fromisoformat(start_time))
            if end_time:
                query = query.filter(cls.timestamp <= datetime.fromisoformat(end_time))
            
            # Execute query and convert to RawDocuments
            results = query.all()
            
            # Convert DAO objects to RawDocuments
            documents = [
                RawDocument(
                    content=doc.content,
                    file_name=doc.file_name,
                    file_size=doc.file_size,
                    timestamp=doc.timestamp.isoformat(),
                    original_file=doc.original_file,
                    chunk_metadata=doc.chunk_metadata
                ) for doc in results
            ]
            
            return documents
        
        finally:
            db.close()

# Use the same credentials as in docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

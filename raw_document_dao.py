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
    file_path = Column(String)
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
                    file_path=doc.file_path,
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

# Use the same credentials as in docker-compose.yml
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

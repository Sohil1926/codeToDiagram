import ast
from typing import Any, Optional, Dict, List

class ProcessedDocument:
    """
    A class representing a processed document with content. A document object contains a chunk of code from a file. 
    """
    def __init__(self, content: str, file_name: str, file_size: int, timestamp: Optional[str] = None, original_file: Optional[str] = None, chunk_metadata: Optional[Dict] = None, embedding: Optional[List[float]] = None):
        """
        Initialize the ProcessedDocument with the given content.
        """
        self.content = content
        self.file_name = file_name
        self.file_size = file_size
        self.timestamp = timestamp
        self.original_file = original_file
        self.embedding = embedding
        self.chunk_metadata = chunk_metadata

  
    


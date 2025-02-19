import ast
from typing import Any, Optional

class RawDocument:
    """
    A class representing a raw document with content. A document object contains a chunk of code from a file. 
    """
    def __init__(self, content: str, file_name: str, file_path: str, file_size: int, ast: Any, metadata: Optional[dict] = None):
        """
        Initialize the RawDocument with the given content.
        """
        self.content = content
        self.file_name = file_name
        self.file_path = file_path
        self.file_size = file_size
        self.ast = ast
        self.metadata = metadata

  
    


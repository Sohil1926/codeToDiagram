from abc import ABC, abstractmethod
from typing import List, Dict, Any
from raw_document import RawDocument

class BaseIngestor(ABC):
    """
    Base class for all ingestors.
    Each source-specific ingestor will inherit from this.
    """
    def __init__(self):
        pass

    @abstractmethod
    def ingest(self) -> List[RawDocument]:
        """Each source-specific ingestor will implement this method"""
        pass

class GitHubIngestor(BaseIngestor):
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token

    def ingest(self) -> List[RawDocument]:
        pass

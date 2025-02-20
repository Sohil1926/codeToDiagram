from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from codebase_map import UniversalAST
from github_reader import fetch_github_files
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
    def __init__(self, url: str, token: str = Optional[str]):
        self.url = url
        self.token = token

    def ingest(self) -> List[RawDocument]:
        files = fetch_github_files(
            url = self.url,
            gh_token=self.token
        )

    
        return [RawDocument(**file) for file in files]

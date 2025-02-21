from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from github_reader import fetch_github_files
from raw_document import RawDocument
from chunking import chunk_file
from datetime import datetime
from utils.tree_sitter_utils import TreeSitterManager
from raw_document_dao import RawDocumentDAO

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
    def __init__(self, url: str, token: Optional[str] = None, max_chars: int = 1500, coalesce: int = 50):
        self.url = url
        self.token = token
        self.max_chars = max_chars
        self.coalesce = coalesce
        self.ts_manager = TreeSitterManager()

    def ingest(self, save_to_db: bool = True) -> List[RawDocument]:
        # Fetch files from GitHub
        files = fetch_github_files(
            repo_url=self.url,
            gh_token=self.token
        )

        # Chunk the files
        chunked_files = []
        for file_info in files:
            # Skip common non-code files
            filename = file_info['name'].lower()
            if (filename.endswith(('.gitignore', 'package-lock.json', 'yarn.lock', 
                                 '.dockerignore', '.env', '.pyc', '.log'))):
                continue

            chunks = chunk_file(
                file_info=file_info,
                parser=self.ts_manager.parser,
                max_chars=self.max_chars,
                coalesce=self.coalesce
            )
            chunked_files.extend(chunks)

        # Create RawDocuments from chunks
        documents = []
        for chunk in chunked_files:
            documents.append(
                RawDocument(
                    content=chunk['content'],
                    file_name=chunk['file_name'],
                    file_path=chunk['file_path'],
                    file_size=len(chunk['content']),
                    timestamp=datetime.utcnow().isoformat(),
                    original_file=chunk['original_file'],
                    chunk_metadata={
                        "chunk_index": chunk['chunk_index'],
                        "start_line": chunk['start_line'],
                        "end_line": chunk['end_line']
                    }
                )
            )
        
        if save_to_db:
            # Save all documents in one batch
            RawDocumentDAO.batch_save(documents)
        
        return documents

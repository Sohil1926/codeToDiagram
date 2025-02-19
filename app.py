import requests
from typing import Dict, List, Any
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
import logging
from ast_processor import parse_ast, extract_metadata
# from embedding_manager import generate_embeddings, store_embeddings, search_embeddings
from llm_handler import generate_prompt, call_llm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

import os
import requests
import zipfile
import io
from urllib.parse import urlparse

def fetch_github_files(url: str, gh_token: str = None) -> list[dict]:
    """
    Fetches files from a GitHub repository using archive download to avoid rate limits.
    Returns list of files with metadata and content.
    """
    # Parse GitHub URL
    parsed = urlparse(url)
    if 'github.com' not in parsed.netloc:
        raise ValueError('Invalid GitHub URL')
    
    path_parts = parsed.path.strip('/').split('/')
    if len(path_parts) < 2:
        raise ValueError('Invalid GitHub repository URL format')
        
    owner, repo = path_parts[:2]
    branch = 'main'  # Default branch - could be parameterized

    # Setup headers with authentication if provided
    headers = {'Accept': 'application/vnd.github.v3+raw'}
    if gh_token:
        headers['Authorization'] = f'token {gh_token}'

    # Get archive URL (single request)
    archive_url = f'https://api.github.com/repos/{owner}/{repo}/zipball/{branch}'
    
    try:
        # Download repository archive
        response = requests.get(archive_url, headers=headers)
        response.raise_for_status()
        
        # Process zip file in memory
        zip_bytes = io.BytesIO(response.content)
        files = []
        
        with zipfile.ZipFile(zip_bytes) as zip_file:
            for file_info in zip_file.infolist():
                if file_info.is_dir():
                    continue
                
                try:
                    with zip_file.open(file_info) as f:
                        content = f.read().decode('utf-8')
                except UnicodeDecodeError:
                    # Skip binary files
                    continue
                
                files.append({
                    'name': os.path.basename(file_info.filename),
                    'file_path': file_info.filename,
                    'file_type': 'file',
                    'content': content,
                    'size': file_info.file_size
                })
        
        print(f"Fetched {len(files)} files from {owner}/{repo}")
        return files

    except requests.HTTPError as e:
        if e.response.status_code == 403:
            reset_time = e.response.headers.get('X-RateLimit-Reset')
            raise RuntimeError(
                f"Rate limit exceeded. Reset at {reset_time} "
                f"(Remaining: {e.response.headers.get('X-RateLimit-Remaining')})"
            )
        raise
    except Exception as e:
        print(f"Error fetching files: {str(e)}")
        raise

def process_code_files(files: List[Dict]) -> None:
    """
    Processes code files through the AST parser and stores embeddings.
    
    Args:
        files (List[Dict]): List of dictionaries containing file information
            Each dict should have 'name' and 'content' keys
    
    Returns:
        None
    
    Raises:
        Exception: If processing or storing fails
    """
    try:
        for file in files:
            logger.info(f"Processing file: {file['name']}")
            
            # Parse AST and extract metadata
            ast = parse_ast(file['content'])
            metadata = extract_metadata(ast)
            
            # Generate embeddings for the file content
            embeddings = generate_embeddings(file['content'])
            
            # Store embeddings with metadata
            store_embeddings(
                embeddings,
                {
                    'file_name': file['name'],
                    'metadata': metadata,
                    'size': file['size']
                }
            )
            
            logger.info(f"Successfully processed and stored embeddings for {file['name']}")
            
    except Exception as e:
        logger.error(f"Error processing files: {str(e)}")
        raise

def query_embeddings(query: str) -> List[Dict]:
    """
    Retrieves relevant documents from the vector database based on the query.
    
    Args:
        query (str): The search query to find relevant code sections
    
    Returns:
        List[Dict]: List of relevant documents with their metadata
    
    Raises:
        Exception: If search fails
    """
    try:
        logger.info(f"Searching embeddings for query: {query}")
        
        # Generate embedding for the query and search
        results = search_embeddings(query, top_k=5)
        
        logger.info(f"Found {len(results)} relevant documents")
        return results
        
    except Exception as e:
        logger.error(f"Error querying embeddings: {str(e)}")
        raise

def generate_mermaid_code(context: List[Dict]) -> str:
    """
    Calls the LLM to generate Mermaid diagram code based on the context.
    
    Args:
        context (List[Dict]): List of relevant code sections and their metadata
    
    Returns:
        str: Generated Mermaid.js diagram code
    
    Raises:
        Exception: If LLM generation fails
    """
    try:
        logger.info("Generating Mermaid diagram code")
        
        # Generate prompt with context
        prompt = generate_prompt(context)
        
        # Call LLM to generate Mermaid code
        mermaid_code = call_llm(prompt)
        
        logger.info("Successfully generated Mermaid diagram code")
        return mermaid_code
        
    except Exception as e:
        logger.error(f"Error generating Mermaid code: {str(e)}")
        raise

def serve_diagram(mermaid_code: str) -> Dict[str, Any]:
    """
    Returns the final diagram to the frontend with additional metadata.
    
    Args:
        mermaid_code (str): The Mermaid.js diagram code
    
    Returns:
        Dict[str, Any]: Dictionary containing diagram code and metadata
            {
                'diagram_code': str,
                'type': 'mermaid',
                'version': str,
                'timestamp': str
            }
    
    Raises:
        Exception: If diagram processing fails
    """
    try:
        logger.info("Preparing diagram for frontend")
        
        from datetime import datetime
        
        response = {
            'diagram_code': mermaid_code,
            'type': 'mermaid',
            'version': '1.0.0',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        logger.info("Successfully prepared diagram response")
        return response
        
    except Exception as e:
        logger.error(f"Error serving diagram: {str(e)}")
        raise

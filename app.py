import requests
from typing import Dict, List, Any
from urllib.parse import urlparse

def fetch_github_files(url: str) -> List[Dict]:
    """
    Fetches files and their contents from a public GitHub repository.
    
    Args:
        url (str): GitHub repository URL (e.g., 'https://github.com/username/repo')
    
    Returns:
        List[Dict]: List of files with their contents
    """
    GITHUB_BASE_URL = 'https://api.github.com'
    
    # Parse GitHub URL
    parsed = urlparse(url)
    if 'github.com' not in parsed.netloc:
        raise ValueError('Not a GitHub URL!')
    
    # Extract owner and repo from path
    owner, repo = parsed.path.strip('/').split('/')
    
    def fetch_directory_contents(path=''):
        """Recursively fetch contents of directories and files."""
        contents_url = f"{GITHUB_BASE_URL}/repos/{owner}/{repo}/contents/{path}"
        response = requests.get(contents_url)
        response.raise_for_status()
        
        files = []
        items = response.json()
        
        # Handle single file response
        if not isinstance(items, list):
            items = [items]
        
        for item in items:
            if item['type'] == 'file':
                # Get the raw content
                if item['download_url']:
                    content_response = requests.get(item['download_url'])
                    content_response.raise_for_status()
                    content = content_response.text
                    
                    files.append({
                        'name': item['path'],
                        'type': 'file',
                        'content': content,
                        'size': item['size']
                    })
                    print(f"Fetched: {item['path']}")
                    
            elif item['type'] == 'dir':
                # Recursively fetch directory contents
                files.extend(fetch_directory_contents(item['path']))
                
        return files
    
    try:
        all_files = fetch_directory_contents()
        print(f"Total files fetched: {len(all_files)}")
        return all_files
        
    except requests.RequestException as e:
        print(f"GitHub API Error: {str(e)}")
        raise
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise

def process_code_files(files: List[Dict]) -> None:
    """Sends files to the processing pipeline."""
    pass

def query_embeddings(query: str) -> List[Dict]:
    """Retrieves relevant documents from the vector database."""
    pass

def generate_mermaid_code(context: List[Dict]) -> str:
    """Calls the LLM to generate Mermaid code."""
    pass

def serve_diagram(mermaid_code: str) -> Dict[str, Any]:
    """Returns the final diagram to the frontend."""
    pass

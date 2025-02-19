import io
import os
from typing import Dict, List
from urllib.parse import urlparse
import zipfile

import requests

def fetch_github_files(url: str, gh_token: str = None) -> List[Dict]:
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
import io
import os
from typing import Dict, List
from urllib.parse import urlparse
import zipfile

import requests

def fetch_github_files(repo_url: str, gh_token: str = None) -> List[Dict]:
    """Fetch files from a GitHub repository"""
    headers = {'Authorization': f'token {gh_token}'} if gh_token else {}
    
    # Try both main and master branches
    branches = ['main', 'master']
    files = []
    
    for branch in branches:
        try:
            # Convert github.com URL to api.github.com
            zip_url = repo_url.replace('github.com', 'api.github.com/repos')
            zip_url = f"{zip_url}/zipball/{branch}"
            
            response = requests.get(zip_url, headers=headers, allow_redirects=True)
            if response.status_code == 200:
                with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
                    for file_info in zip_file.filelist:
                        try:
                            with zip_file.open(file_info) as file:
                                content = file.read().decode('utf-8')
                                files.append({
                                    'name': file_info.filename.split('/', 1)[1],
                                    'content': content,
                                    'branch': branch,
                                    'size': file_info.file_size
                                })
                        except (UnicodeDecodeError, IndexError):
                            continue
                return files
                
        except Exception as e:
            if branch == branches[-1]:  # Only raise error if both branches fail
                raise Exception(f"Failed to fetch repository: {str(e)}")
            continue
            
    return files
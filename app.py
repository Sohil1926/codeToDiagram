from typing import Dict, List, Any
from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
import logging
from datetime import datetime
from codebase_map import CodebaseMapper
from github_reader import fetch_github_files
from llm_handler import generate_initial_diagram, generate_question_diagram
from raw_document import RawDocument
from ingestor import GitHubIngestor
from processor import GitHubProcessor
from embedding_manager import OpenAIEmbedder
from processed_document_dao import ProcessedDocumentDAO
import json
from dotenv import load_dotenv

load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8001"],  # Allow both ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize CodebaseMapper
codebase_mapper = CodebaseMapper()

def query_embeddings(query: str) -> List[Dict]:
    """
    Retrieves relevant documents from the vector database based on the query.
    """
    try:
        dao = ProcessedDocumentDAO(embedder=OpenAIEmbedder())
        results = dao.search(query, top_k=5)
        return results
    except Exception as e:
        logger.error(f"Error querying embeddings: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate_diagram")
async def generate_diagram(url: str = Body(..., embed=True)):
    """
    Endpoint to generate an initial diagram from a GitHub repository URL.
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)  
        if not all([parsed_url.scheme, parsed_url.netloc]) or 'github.com' not in parsed_url.netloc:
            raise HTTPException(status_code=400, detail="Invalid GitHub URL")

        # Fetch GitHub files
        files = fetch_github_files(repo_url=url)
        
        # Generate codebase map
        repo_map = codebase_mapper.generate_repo_map(files)
        
        # Process and store files for future questions if not already done
        github_ingestor = GitHubIngestor(url=url) 
        raw_docs = github_ingestor.ingest()
        
        processor = GitHubProcessor(embedder=OpenAIEmbedder())
        processed_docs = processor.process(raw_docs)
        
        # Now create the initial diagram using the codebase map
        diagram_code = generate_initial_diagram(repo_map)
        
        return {"diagram_code": diagram_code}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in generate_diagram: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask_question")
async def ask_question(question: str = Body(..., embed=True)):
    """
    Endpoint to handle follow-up questions and generate new diagrams.
    """
    try:
        # Search for relevant code sections using the question
        relevant_docs = query_embeddings(question)
        
        # Generate new diagram based on question and relevant code
        diagram_code = generate_question_diagram(question, relevant_docs)
        
        return {"diagram_code": diagram_code}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in ask_question: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
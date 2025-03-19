from typing import List, Dict, Any
import logging
import os
from anthropic import Anthropic
from utils.prompts import GENERATE_DIAGRAM_PROMPT, INITIAL_DIAGRAM_PROMPT, QUESTION_DIAGRAM_PROMPT
from processed_document import ProcessedDocument

logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_initial_diagram(codebase_map: str) -> str:
    """
    Calls the Anthropic Claude API to generate an initial architecture diagram
    based on the codebase map.
    """
    try:
        # Create the prompt with the codebase map
        prompt = INITIAL_DIAGRAM_PROMPT.format(codebase_map=codebase_map)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=GENERATE_DIAGRAM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=5000,
            temperature=0.3,
        )
        
        # Extract Mermaid code from response
        full_response = response.content[0].text
        return full_response
        
    except Exception as e:
        logger.error(f"Error calling LLM for initial diagram: {str(e)}")
        raise

def generate_question_diagram(question: str, relevant_docs: List[ProcessedDocument]) -> str:
    """
    Calls the Anthropic Claude API to generate a diagram that answers a specific question
    using relevant code context.
    """
    try:
        # Extract content from relevant documents
        code_context = "\n\n".join([f"File: {doc.file_name}\n{doc.content}" for doc in relevant_docs])
        
        # Create the prompt with the question and code context
        prompt = QUESTION_DIAGRAM_PROMPT.format(
            question=question,
            code_context=code_context
        )
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system=GENERATE_DIAGRAM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=5000,
            temperature=0.3,
        )
        
        # Extract Mermaid code from response
        full_response = response.content[0].text
        return full_response
        
    except Exception as e:
        logger.error(f"Error calling LLM for question diagram: {str(e)}")
        raise

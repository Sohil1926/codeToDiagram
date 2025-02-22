from typing import List, Dict, Any
import logging
import os
from openai import OpenAI

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_prompt(context: List[Dict[str, Any]]) -> str:
    """
    Generates a prompt for the LLM to create a Mermaid diagram.
    
    Args:
        context (List[Dict]): List of dictionaries containing code metadata and content
    
    Returns:
        str: The generated prompt
    """
    try:
        # Extract relevant information from the context dictionaries
        code_sections = []
        
        for item in context:
            if 'metadata' in item:
                metadata = item['metadata']
                if isinstance(metadata, dict) and 'functions' in metadata:
                    # Handle search results
                    for func in metadata['functions']:
                        code_sections.append(f"Function: {func['name']}\nDocstring: {func['docstring']}")
                else:
                    # Handle map content
                    code_sections.append(str(metadata))
        
        # Join all sections with newlines
        combined_sections = "\n\n".join(code_sections)
        
        prompt = f"""Generate a Mermaid.js diagram showing the relationships between components in this codebase.

Code Sections:
{combined_sections}

Requirements:
1. Use appropriate Mermaid.js syntax (preferably classDiagram)
2. Show relationships between components (inheritance, composition, dependencies)
3. Include brief descriptions where relevant
4. Use appropriate Mermaid notation for different relationships
5. Make the diagram clear and readable
6. Focus on the main classes, functions, and their relationships

Generate only the Mermaid.js code without any explanation or additional text."""
        
        return prompt
        
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}")
        raise

def call_llm(prompt: str) -> str:
    """
    Calls the OpenAI API to generate Mermaid diagram code.
    
    Args:
        prompt (str): The prompt for the LLM
    
    Returns:
        str: Generated Mermaid.js diagram code
    """
    try:
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a technical diagram expert who creates Mermaid.js diagrams from code analysis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        # Extract and clean the Mermaid code
        
        # Ensure it starts with graph or flowchart
        # if not any(mermaid_code.startswith(prefix) for prefix in ['graph', 'flowchart', 'classDiagram']):
        #     raise ValueError("Generated code is not valid Mermaid.js syntax")
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        logger.error(f"Error calling LLM: {str(e)}")
        raise

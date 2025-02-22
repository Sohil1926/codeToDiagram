from typing import List, Dict, Any
import logging
import os
from anthropic import Anthropic

logger = logging.getLogger(__name__)

# Initialize Anthropic client
client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def generate_prompt(context: List[Dict[str, Any]], user_question: str) -> str:
    """
    Generates a prompt for the LLM to create a Mermaid diagram that answers the user's question.
    
    Args:
        context (List[Dict]): List of dictionaries containing code metadata and content
        user_question (str): The question from the user that the diagram should answer
    
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
        
        prompt = f"""Generate a Mermaid.js diagram that answers the following question:
{user_question}

Use the following code context to create the diagram:
{combined_sections}

Requirements:
1. Use appropriate Mermaid.js syntax (preferably classDiagram)
2. Show only the components and relationships relevant to answering the question
3. Include brief descriptions where they help answer the question
4. Use appropriate Mermaid notation for different relationships
5. Make the diagram clear and focused on answering the question
6. Omit any components that aren't relevant to the question

Generate only the Mermaid.js code without any explanation or additional text."""
        
        return prompt
        
    except Exception as e:
        logger.error(f"Error generating prompt: {str(e)}")
        raise

def call_llm(prompt: str) -> str:
    """
    Calls the Anthropic Claude API to generate Mermaid diagram code.
    """
    try:
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system="You are a technical diagram expert who creates Mermaid.js diagrams to answer questions about code. Return ONLY valid Mermaid 10.2 code wrapped in <mermaid> tags.",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.3,
            stop_sequences=["</mermaid>"]
        )
        
        # Extract Mermaid code from response
        full_response = response.content[0].text
        if "<mermaid>" in full_response:
            return full_response.split("<mermaid>")[1].split("</mermaid>")[0].strip()
        return full_response  # Fallback if tags missing
        
    except Exception as e:
        logger.error(f"Error calling LLM: {str(e)}")
        raise

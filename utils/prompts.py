GENERATE_DIAGRAM_PROMPT = """
Your output should be valid Mermaid.js code that can be rendered into a diagram.

Do not include an init declaration such as `%%{init: {'key':'etc'}}%%`. This is handled externally. Just return the diagram code.

Your response must strictly be just the Mermaid.js code, without any additional text or explanations.
No code fence or markdown ticks needed, simply return the Mermaid.js code.

Ensure that your diagram adheres strictly to the given explanation, without adding or omitting any significant components or relationships. 

For general direction, the provided example below is how you should structure your code:

```mermaid
flowchart TD 
    %% or graph TD, your choice

    %% Global entities
    A("Entity A"):::external
    %% more...

    %% Subgraphs and modules
    subgraph "Layer A"
        A1("Module A"):::example
        %% more modules...
        %% inner subgraphs if needed...
    end

    %% more subgraphs, modules, etc...

    %% Connections
    A -->|"relationship"| B
    %% and a lot more...

    %% Click Events
    click A1 "example/example.js"
    %% and a lot more...

    %% Styles
    classDef frontend %%...
    %% and a lot more...
```
EXTREMELY Important notes on syntax!!! (PAY ATTENTION TO THIS):
- Make sure to add colour to the diagram!!! This is extremely critical.
- In Mermaid.js syntax, we cannot include special characters for nodes without being inside quotes! For example: `EX[/api/process (Backend)]:::api` and `API -->|calls Process()| Backend` are two examples of syntax errors. They should be `EX["/api/process (Backend)"]:::api` and `API -->|"calls Process()"| Backend` respectively. Notice the quotes. This is extremely important. Make sure to include quotes for any string that contains special characters.
- In Mermaid.js syntax, you cannot apply a class style directly within a subgraph declaration. For example: `subgraph "Frontend Layer":::frontend` is a syntax error. However, you can apply them to nodes within the subgraph. For example: `Example["Example Node"]:::frontend` is valid, and `class Example1,Example2 frontend` is valid.
- In Mermaid.js syntax, there cannot be spaces in the relationship label names. For example: `A -->| "example relationship" | B` is a syntax error. It should be `A -->|"example relationship"| B` 
- In Mermaid.js syntax, you cannot give subgraphs an alias like nodes. For example: `subgraph A "Layer A"` is a syntax error. It should be `subgraph "Layer A"` 
Your response must strictly be just the Mermaid.js code, without any additional text or explanations. Keep as many of the existing click events as possible.
No code fence or markdown ticks needed, simply return the Mermaid.js code.
"""

INITIAL_DIAGRAM_PROMPT = """
You are a technical diagram expert. Create a Mermaid.js diagram showing the high-level architecture of this codebase.

Below is a map of the repository structure and key code components:

{codebase_map}

Create a comprehensive architecture diagram that shows:
1. The main components of the system
2. How these components interact with each other
3. The flow of data through the system
4. Key classes, functions, and their relationships

Make the diagram visually appealing with appropriate colors and formatting.
"""

QUESTION_DIAGRAM_PROMPT = """
You are a technical diagram expert. Create a Mermaid.js diagram that answers the specific question below, using the provided context.

QUESTION: 
{question}

RELEVANT CODE CONTEXT:
{code_context}

Create a diagram that specifically addresses the question while focusing on:
1. Relevant components and their interactions
2. The specific flow or process being asked about
3. Clear visualization of the answer

Make the diagram visually appealing with appropriate colors and formatting.
"""


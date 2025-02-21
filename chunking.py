import logging
from typing import List, Dict
from dataclasses import dataclass
from tree_sitter import Tree, Node, Parser, Language
import re

logger = logging.getLogger(__name__)

@dataclass
class Span:
    start: int
    end: int

    def extract(self, s: bytes) -> bytes:
        """Grab the corresponding substring of string s by bytes"""
        return s[self.start:self.end]
    
    def extract_lines(self, s: str) -> str:
        """Extract lines between start and end line numbers"""
        return "\n".join(s.splitlines()[self.start:self.end])

    def __add__(self, other: 'Span') -> 'Span':
        """Concatenate spans, e.g., Span(1,2) + Span(2,4) = Span(1,4)"""
        return Span(min(self.start, other.start), max(self.end, other.end))

    def __len__(self) -> int:
        return self.end - self.start

def get_line_number(byte_offset: int, source_code: bytes) -> int:
    """Convert byte offset to line number"""
    return source_code.count(b'\n', 0, byte_offset) + 1

def non_whitespace_len(text: bytes) -> int:
    """Get length of text excluding all whitespace"""
    decoded = text.decode('utf-8')
    return len(re.sub(r'\s', '', decoded))

def chunker(
    tree: Tree,
    source_code: bytes,
    max_chars: int = 512 * 3,
    coalesce: int = 50
) -> List[Span]:
    # 1. Recursively form chunks
    def chunk_node(node: Node) -> List[Span]:
        chunks: List[Span] = []
        current_chunk = Span(node.start_byte, node.start_byte)
        node_children = node.children
        
        for child in node_children:
            if child.end_byte - child.start_byte > max_chars:
                chunks.append(current_chunk)
                current_chunk = Span(child.end_byte, child.end_byte)
                chunks.extend(chunk_node(child))
            elif child.end_byte - child.start_byte + len(current_chunk) > max_chars:
                chunks.append(current_chunk)
                current_chunk = Span(child.start_byte, child.end_byte)
            else:
                current_chunk += Span(child.start_byte, child.end_byte)
        chunks.append(current_chunk)
        return chunks

    chunks = chunk_node(tree.root_node)

    # 2. Fill gaps between chunks
    for prev, curr in zip(chunks[:-1], chunks[1:]):
        prev.end = curr.start
    if chunks:
        chunks[-1].end = tree.root_node.end_byte

    # 3. Combine small chunks
    new_chunks = []
    current_chunk = Span(0, 0)
    for chunk in chunks:
        current_chunk += chunk
        if (non_whitespace_len(current_chunk.extract(source_code)) > coalesce and 
            b'\n' in current_chunk.extract(source_code)):
            new_chunks.append(current_chunk)
            current_chunk = Span(chunk.end, chunk.end)
    if len(current_chunk) > 0:
        new_chunks.append(current_chunk)

    # 4. Convert to line numbers
    line_chunks = [
        Span(
            get_line_number(chunk.start, source_code),
            get_line_number(chunk.end, source_code)
        ) for chunk in new_chunks
    ]

    # 5. Remove empty chunks
    line_chunks = [chunk for chunk in line_chunks if len(chunk) > 0]

    return line_chunks

def chunk_file(
    file_info: Dict,
    parser: Parser,
    max_chars: int = 1500,
    coalesce: int = 50
) -> List[Dict]:
    """Wrapper function that handles file parsing and chunk formatting."""
    if 'name' not in file_info or 'content' not in file_info:
        logger.warning("file_info missing 'name' or 'content'. Skipping...")
        return []

    file_name = file_info['name']
    content = file_info['content']
    source_bytes = content.encode('utf-8')

    try:
        tree = parser.parse(source_bytes)
        chunks = chunker(tree, source_bytes, max_chars, coalesce)
    except Exception as e:
        logger.error(f"Failed to parse {file_name}: {str(e)}")
        return []

    result_chunks = []
    for i, chunk in enumerate(chunks):
        chunk_content = "\n".join(content.splitlines()[chunk.start-1:chunk.end])
        if not chunk_content.strip():
            continue

        result_chunks.append({
            'content': chunk_content.strip(),
            'file_name': file_name,
            'file_path': file_info.get('path', ''),
            'chunk_index': i,
            'original_file': file_name,
            'start_line': chunk.start,
            'end_line': chunk.end
        })

    return result_chunks

import os
from pathlib import Path
from tree_sitter import Language, Parser, Node
from typing import Dict, List
import warnings
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Suppress Tree-sitter warnings
warnings.filterwarnings("ignore", category=UserWarning)

class CodebaseMapper:
    def __init__(self):
        self.parser = Parser()
        logger.debug("Initializing RepoMapper")
        self.language_map = self._load_languages()
        self.query_map = self._load_queries()
        logger.debug(f"Loaded languages: {list(self.language_map.keys())}")
        logger.debug(f"Loaded queries: {list(self.query_map.keys())}")
        
    def _load_languages(self) -> Dict[str, Language]:
        """Load all Tree-sitter language parsers"""
        languages = {}
        lang_dir = Path("vendor")
        logger.debug(f"Looking for language parsers in {lang_dir}")
        
        if not lang_dir.exists():
            logger.error(f"Vendor directory not found at {lang_dir}")
            return languages
        
        for lang_path in lang_dir.glob("tree-sitter-*"):
            lang_name = lang_path.name.split("-", 2)[-1]
            lib_path = f"build/{lang_name}.so"
            logger.debug(f"Processing language: {lang_name}")
            
            try:
                if not Path(lib_path).exists():
                    logger.debug(f"Building language library for {lang_name}")
                    Language.build_library(lib_path, [str(lang_path)])
                
                languages[lang_name] = Language(lib_path, lang_name)
                logger.debug(f"Successfully loaded {lang_name}")
            except Exception as e:
                logger.error(f"Error loading language {lang_name}: {str(e)}")
            
        return languages
    
    def _load_queries(self) -> Dict[str, str]:
        """Load Tree-sitter query files for each language"""
        queries = {}
        query_dir = Path("queries")
        logger.debug(f"Looking for queries in {query_dir}")
        
        if not query_dir.exists():
            logger.error(f"Query directory not found at {query_dir}")
            return queries
        
        for query_file in query_dir.glob("*-tags.scm"):
            lang_name = query_file.name.split("-")[0]
            logger.debug(f"Loading query for {lang_name}")
            queries[lang_name] = query_file.read_text()
            
        return queries
    
    def _get_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower().lstrip('.')
        lang_map = {
            'js': 'javascript', 'jsx': 'javascript',
            'py': 'python', 'java': 'java',
            'go': 'go', 'rs': 'rust',
            'ts': 'typescript', 'tsx': 'typescript',
            'rb': 'ruby'
        }
        detected_lang = lang_map.get(ext, ext)
        logger.debug(f"Detected language {detected_lang} for file {file_path}")
        return detected_lang
    
    def _get_code_snippet(self, content: str, node: Node) -> str:
        """Extract relevant code snippet with context"""
        start_line = node.start_point[0]
        end_line = node.end_point[0]
        lines = content.split('\n')
        
        # Show 2 lines before and after
        context_start = max(0, start_line - 2)
        context_end = min(len(lines), end_line + 3)
        
        snippet = []
        for i in range(context_start, context_end):
            prefix = "⋮..." if i == context_start else f"{i+1:4}"
            prefix = "│   " if context_start < i < context_end-1 else prefix
            snippet.append(f"{prefix} {lines[i]}")
            
        return '\n'.join(snippet)
    
    def _process_file(self, file: Dict) -> List[str]:
        """Process a single file to extract key symbols"""
        lang_name = self._get_language(file['name'])  
        logger.debug(f"Processing file {file['name']} with language {lang_name}")
        
        if lang_name not in self.language_map:
            logger.warning(f"No parser available for language {lang_name}")
            return []
            
        self.parser.set_language(self.language_map[lang_name])
        try:
            tree = self.parser.parse(bytes(file['content'], "utf8"))
            logger.debug(f"Successfully parsed {file['name']}")
        except Exception as e:
            logger.error(f"Error parsing {file['name']}: {str(e)}")
            return []
        
        # Get language-specific query
        query = self.query_map.get(lang_name, "")
        if not query:
            logger.warning(f"No query available for language {lang_name}")
            return []
            
        try:
            captures = self.language_map[lang_name].query(query).captures(tree.root_node)
            logger.debug(f"Found {len(captures)} captures in {file['name']}")
        except Exception as e:
            logger.error(f"Error querying {file['name']}: {str(e)}")
            return []
        
        symbols = []
        seen = set()
        for node, tag in captures:
            snippet = self._get_code_snippet(file['content'], node)
            if snippet not in seen:
                # Add both snippet and tag type
                symbols.append(f"{tag}: {snippet}")
                seen.add(snippet)
                
        logger.debug(f"Extracted {len(symbols)} symbols from {file['name']}")
        return symbols
    
    def generate_repo_map(self, files: List[Dict]) -> str:
        """Main entry point to generate repo map"""
        
        repo_map = []
        
        for file in files:
            if not file['content'].strip():
                logger.debug(f"Skipping empty file {file['name']}")
                continue
                
            symbols = self._process_file(file)
            if not symbols:
                logger.debug(f"No symbols found in {file['name']}")
                continue
                
            header = f"\n{file['name']}:\n"
            repo_map.append(header + '\n'.join(symbols))
            
        result = '\n'.join(repo_map)
        logger.info(f"Generated repo map with {len(repo_map)} files")
        return result[:8000]  # Limit to typical context window size


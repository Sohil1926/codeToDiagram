import logging
from pathlib import Path
from typing import Dict
from tree_sitter import Language, Parser
import warnings

logger = logging.getLogger(__name__)
warnings.filterwarnings("ignore", category=UserWarning)

class TreeSitterManager:
    def __init__(self):
        self.parser = Parser()
        self.language_map = self._load_languages()
        
        # Set a default language (e.g., javascript) if available
        if self.language_map:
            default_lang = next(iter(self.language_map.values()))
            self.parser.set_language(default_lang)
        
        logger.debug(f"Loaded languages: {list(self.language_map.keys())}")

    def _load_languages(self) -> Dict[str, Language]:
        """Load all Tree-sitter language parsers"""
        languages = {}
        lang_dir = Path("vendor")
        logger.debug(f"Looking for language parsers in {lang_dir}")
        
        if not lang_dir.exists():
            logger.error(f"Vendor directory not found at {lang_dir}")
            return languages
        
        # Define language variants
        lang_variants = {
            'javascript': ['javascript', 'javascript.jsx'],
            'typescript': ['typescript', 'typescript.tsx']
        }
        
        for lang_path in lang_dir.glob("tree-sitter-*"):
            base_lang = lang_path.name.split("-", 2)[-1]
            lib_path = f"build/{base_lang}.so"
            logger.debug(f"Processing language: {base_lang}")
            
            try:
                if not Path(lib_path).exists():
                    logger.debug(f"Building language library for {base_lang}")
                    Language.build_library(lib_path, [str(lang_path)])
                
                # Load base language
                lang = Language(lib_path, base_lang)
                languages[base_lang] = lang
                
                # Load variants if they exist
                if base_lang in lang_variants:
                    for variant in lang_variants[base_lang]:
                        languages[variant] = lang
                    
                logger.debug(f"Successfully loaded {base_lang}")
            except Exception as e:
                logger.error(f"Error loading language {base_lang}: {str(e)}")
            
        return languages

    def get_language(self, file_path: str) -> str:
        """Detect language from file extension"""
        ext = Path(file_path).suffix.lower().lstrip('.')
        lang_map = {
            'js': 'javascript',
            'jsx': 'javascript.jsx',  # Use JSX parser for .jsx files
            'ts': 'typescript',
            'tsx': 'typescript.tsx',  # Use TSX parser for .tsx files
            'py': 'python',
            'java': 'java',
            'go': 'go',
            'rs': 'rust',
            'rb': 'ruby'
        }
        detected_lang = lang_map.get(ext, ext)
        logger.debug(f"Detected language {detected_lang} for file {file_path}")
        return detected_lang

    def set_language(self, lang_name: str) -> None:
        """Set the parser's language"""
        if lang_name not in self.language_map:
            raise ValueError(f"No parser available for language {lang_name}")
        self.parser.set_language(self.language_map[lang_name])

    def parse_file(self, file_path: str, content: str) -> Parser:
        """Parse file content with appropriate language parser"""
        lang_name = self.get_language(file_path)
        self.set_language(lang_name)  # Use the new set_language method
        return self.parser.parse(bytes(content, "utf8"))
"""Utility functions for the Cerebras Code Scanner.

This module contains utility functions for logging, configuration, code chunking,
and other helper functions.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Union

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Set up logging configuration.
    
    Args:
        log_level: The logging level (default: INFO).
        
    Returns:
        A configured logger instance.
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler(logs_dir / "scanner.log"),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger("cerebras_scanner")

def load_config(config_path: Union[str, Path] = "config.json") -> Dict[str, Any]:
    """Load configuration from a JSON file.
    
    Args:
        config_path: Path to the configuration file.
        
    Returns:
        A dictionary containing the configuration.
    """
    config_path = Path(config_path)
    
    # Use default config if file doesn't exist
    if not config_path.exists():
        logging.warning(f"Config file not found: {config_path}. Using default configuration.")
        return {
            "cerebras_api_key": os.environ.get("CEREBRAS_API_KEY", ""),
            "model_name": "llama-4",
            "max_chunk_tokens": 4000,
            "max_response_tokens": 2048,
            "temperature": 0.2,
            "top_p": 0.95,
            "prompts_file": "docs/proprompts.json"
        }
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config
    except Exception as e:
        logging.error(f"Error loading config from {config_path}: {str(e)}")
        raise

def get_file_language(file_path: Path) -> str:
    """Determine the programming language of a file based on its extension.
    
    Args:
        file_path: Path to the file.
        
    Returns:
        The programming language name.
    """
    extension = file_path.suffix.lower()
    
    if extension == ".py":
        return "Python"
    elif extension in [".sql"]:
        return "SQL"
    else:
        return "Unknown"

def chunk_code(code: str, max_tokens: int = 4000) -> List[str]:
    """Split code into manageable chunks for processing.
    
    This is a simple implementation that splits code by lines to avoid
    exceeding token limits. A more sophisticated implementation would
    use a tokenizer to count actual tokens.
    
    Args:
        code: The code to split into chunks.
        max_tokens: Maximum number of tokens per chunk (approximate).
        
    Returns:
        A list of code chunks.
    """
    # Simple approximation: assume average of 5 characters per token
    max_chars = max_tokens * 5
    
    # If code is small enough, return it as a single chunk
    if len(code) <= max_chars:
        return [code]
    
    lines = code.split("\n")
    chunks = []
    current_chunk = []
    current_size = 0
    
    for line in lines:
        line_size = len(line) + 1  # +1 for newline
        
        # If adding this line would exceed the limit, start a new chunk
        if current_size + line_size > max_chars and current_chunk:
            chunks.append("\n".join(current_chunk))
            current_chunk = []
            current_size = 0
        
        # Add the line to the current chunk
        current_chunk.append(line)
        current_size += line_size
    
    # Add the last chunk if it's not empty
    if current_chunk:
        chunks.append("\n".join(current_chunk))
    
    return chunks

def extract_function_chunks(code: str) -> List[str]:
    """Extract individual functions from Python code.
    
    This is a more sophisticated chunking method that tries to keep
    functions together as logical units.
    
    Args:
        code: The Python code to split into function chunks.
        
    Returns:
        A list of code chunks, each containing a function or class.
    """
    import re
    
    # Pattern to match function or class definitions
    pattern = r"(\s*def\s+\w+\s*\(.*?\)\s*:.*?(?=\s*def\s+|\s*class\s+|$)" + \
              r"|\s*class\s+\w+.*?(?=\s*def\s+|\s*class\s+|$))"
    
    # Find all matches
    matches = re.findall(pattern, code, re.DOTALL)
    
    # If no matches (no functions or classes), return the whole code as one chunk
    if not matches:
        return [code]
    
    # Extract the code before the first function/class
    first_match_start = code.find(matches[0].lstrip())
    if first_match_start > 0:
        preamble = code[:first_match_start].strip()
        if preamble:
            matches.insert(0, preamble)
    
    return matches
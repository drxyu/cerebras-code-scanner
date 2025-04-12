"""Code Analyzer module for the Cerebras Code Scanner.

This module contains the CodeAnalyzer class that is responsible for scanning Python code
for security vulnerabilities and performance issues using Cerebras-hosted Llama 4 model.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
import logging

from cerebras.cloud.sdk import CerebrasCloudSDK
from scanner.prompt_manager import PromptManager
from scanner.utils import chunk_code, get_file_language

logger = logging.getLogger(__name__)

class CodeAnalyzer:
    """Analyzes code for security vulnerabilities and performance issues.
    
    This class is responsible for scanning Python code and identifying potential
    security vulnerabilities and performance issues using the Cerebras-hosted
    Llama 4 model.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the CodeAnalyzer.
        
        Args:
            config: Configuration dictionary containing API keys and settings.
        """
        self.config = config
        self.prompt_manager = PromptManager(config.get("prompts_file", "docs/proprompts.json"))
        
        # Initialize Cerebras SDK
        api_key = config.get("cerebras_api_key") or os.environ.get("CEREBRAS_API_KEY")
        if not api_key:
            raise ValueError("Cerebras API key not found. Please set it in the config file or as an environment variable.")
        
        self.cerebras_sdk = CerebrasCloudSDK(api_key=api_key)
        self.model_name = config.get("model_name", "llama-4")
        
        logger.info(f"CodeAnalyzer initialized with model: {self.model_name}")
    
    def scan_codebase(self, path: Union[str, Path], categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """Scan a codebase for security vulnerabilities and performance issues.
        
        Args:
            path: Path to the file or directory to scan.
            categories: Optional list of specific vulnerability categories to scan for.
            
        Returns:
            A dictionary containing the scan results.
        """
        path = Path(path)
        results = {
            "issues": [],
            "stats": {
                "files_scanned": 0,
                "total_issues": 0,
                "categories": {}
            }
        }
        
        if path.is_file():
            # Scan a single file
            file_results = self.scan_file(path, categories)
            results["issues"].extend(file_results)
            results["stats"]["files_scanned"] = 1
        elif path.is_dir():
            # Scan all Python and SQL files in the directory
            for pattern in ["**/*.py", "**/*.sql"]:
                for file_path in path.glob(pattern):
                    logger.info(f"Scanning file: {file_path}")
                    file_results = self.scan_file(file_path, categories)
                    results["issues"].extend(file_results)
                    results["stats"]["files_scanned"] += 1
        else:
            logger.error(f"Invalid path: {path}")
            return results
        
        # Update statistics
        results["stats"]["total_issues"] = len(results["issues"])
        
        # Count issues by category
        for issue in results["issues"]:
            category = issue["category"]
            if category not in results["stats"]["categories"]:
                results["stats"]["categories"][category] = 0
            results["stats"]["categories"][category] += 1
        
        return results
    
    def scan_file(self, file_path: Path, categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Scan a single file for security vulnerabilities and performance issues.
        
        Args:
            file_path: Path to the file to scan.
            categories: Optional list of specific vulnerability categories to scan for.
            
        Returns:
            A list of issues found in the file.
        """
        issues = []
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                code = f.read()
            
            language = get_file_language(file_path)
            if language not in ["Python", "SQL"]:
                logger.warning(f"Unsupported language for file: {file_path}")
                return issues
            
            # Get relevant prompts for this file type
            prompts = self.prompt_manager.get_prompts(language, categories)
            if not prompts:
                logger.warning(f"No prompts found for language: {language}")
                return issues
            
            # Split code into manageable chunks if it's too large
            code_chunks = chunk_code(code, max_tokens=self.config.get("max_chunk_tokens", 4000))
            
            # Process each chunk with each relevant prompt
            for i, chunk in enumerate(code_chunks):
                chunk_issues = self._process_code_chunk(chunk, prompts, file_path, chunk_index=i)
                issues.extend(chunk_issues)
        
        except Exception as e:
            logger.error(f"Error scanning file {file_path}: {str(e)}")
        
        return issues
    
    def _process_code_chunk(self, code: str, prompts: List[Dict[str, Any]], 
                           file_path: Path, chunk_index: int = 0) -> List[Dict[str, Any]]:
        """Process a chunk of code with multiple prompts.
        
        Args:
            code: The code chunk to analyze.
            prompts: List of prompt templates to use.
            file_path: Path to the file being analyzed.
            chunk_index: Index of the chunk in the file.
            
        Returns:
            A list of issues found in the code chunk.
        """
        issues = []
        
        for prompt_template in prompts:
            category = prompt_template["category"]
            subcategory = prompt_template["subcategory"]
            
            # Create the 2nd-layer prompt by inserting the code
            prompt = f"{prompt_template['prompt_template']}\n\nCode:\n```{prompt_template['language'].lower()}\n{code}\n```"
            
            # Call Cerebras API with the prompt
            try:
                response = self._call_cerebras_api(prompt)
                
                # Parse the response to extract issues
                parsed_issues = self._parse_response(response, category, subcategory, file_path, chunk_index)
                issues.extend(parsed_issues)
                
            except Exception as e:
                logger.error(f"Error processing prompt {category}/{subcategory}: {str(e)}")
        
        return issues
    
    def _call_cerebras_api(self, prompt: str) -> str:
        """Call the Cerebras API with a prompt.
        
        Args:
            prompt: The prompt to send to the model.
            
        Returns:
            The model's response as a string.
        """
        try:
            # Call the Cerebras API using the SDK
            response = self.cerebras_sdk.generate(
                model=self.model_name,
                prompt=prompt,
                max_tokens=self.config.get("max_response_tokens", 2048),
                temperature=self.config.get("temperature", 0.2),
                top_p=self.config.get("top_p", 0.95),
            )
            
            # Extract the generated text from the response
            return response.generated_text
            
        except Exception as e:
            logger.error(f"Error calling Cerebras API: {str(e)}")
            raise
    
    def _parse_response(self, response: str, category: str, subcategory: str, 
                       file_path: Path, chunk_index: int) -> List[Dict[str, Any]]:
        """Parse the model's response to extract issues.
        
        Args:
            response: The model's response text.
            category: The vulnerability category.
            subcategory: The vulnerability subcategory.
            file_path: Path to the file being analyzed.
            chunk_index: Index of the chunk in the file.
            
        Returns:
            A list of issues extracted from the response.
        """
        issues = []
        
        # Skip if the response indicates no issues
        if "no issues" in response.lower() or "no vulnerabilities" in response.lower():
            return issues
        
        # Extract bullet points from markdown response
        bullet_pattern = r'\s*[-*]\s+(.+?)(?=\s*[-*]\s+|$)'
        bullets = re.findall(bullet_pattern, response, re.DOTALL)
        
        for bullet in bullets:
            # Skip empty bullets
            if not bullet.strip():
                continue
                
            # Create an issue entry
            issue = {
                "category": category,
                "subcategory": subcategory,
                "description": bullet.strip(),
                "file_path": str(file_path),
                "chunk_index": chunk_index,
                "raw_response": response
            }
            
            issues.append(issue)
        
        return issues
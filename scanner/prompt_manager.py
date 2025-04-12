"""Prompt Manager module for the Cerebras Code Scanner.

This module contains the PromptManager class that is responsible for loading and managing
prompt templates for different vulnerability categories.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class PromptManager:
    """Manages prompt templates for different vulnerability categories.
    
    This class is responsible for loading prompt templates from a JSON file and
    providing appropriate prompts for different languages and vulnerability categories.
    """
    
    def __init__(self, prompts_file: str):
        """Initialize the PromptManager.
        
        Args:
            prompts_file: Path to the JSON file containing prompt templates.
        """
        self.prompts_file = prompts_file
        self.prompts = self._load_prompts()
        
        # Group prompts by language for faster access
        self.prompts_by_language = {}
        for prompt in self.prompts:
            language = prompt["language"]
            if language not in self.prompts_by_language:
                self.prompts_by_language[language] = []
            self.prompts_by_language[language].append(prompt)
        
        logger.info(f"Loaded {len(self.prompts)} prompt templates from {prompts_file}")
    
    def _load_prompts(self) -> List[Dict[str, Any]]:
        """Load prompt templates from the JSON file.
        
        Returns:
            A list of prompt template dictionaries.
        """
        try:
            with open(self.prompts_file, "r", encoding="utf-8") as f:
                prompts = json.load(f)
            return prompts
        except Exception as e:
            logger.error(f"Error loading prompts from {self.prompts_file}: {str(e)}")
            return []
    
    def get_prompts(self, language: str, categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Get prompt templates for a specific language and categories.
        
        Args:
            language: The programming language to get prompts for.
            categories: Optional list of specific vulnerability categories to include.
            
        Returns:
            A list of prompt template dictionaries.
        """
        if language not in self.prompts_by_language:
            logger.warning(f"No prompts found for language: {language}")
            return []
        
        prompts = self.prompts_by_language[language]
        
        # Filter by categories if specified
        if categories:
            prompts = [p for p in prompts if p["category"] in categories]
        
        return prompts
    
    def get_prompt_by_category(self, language: str, category: str, subcategory: str) -> Optional[Dict[str, Any]]:
        """Get a specific prompt template by category and subcategory.
        
        Args:
            language: The programming language.
            category: The vulnerability category.
            subcategory: The vulnerability subcategory.
            
        Returns:
            A prompt template dictionary, or None if not found.
        """
        for prompt in self.prompts:
            if (prompt["language"] == language and 
                prompt["category"] == category and 
                prompt["subcategory"] == subcategory):
                return prompt
        
        logger.warning(f"No prompt found for {language}/{category}/{subcategory}")
        return None
    
    def get_categories(self, language: str) -> List[str]:
        """Get all available vulnerability categories for a language.
        
        Args:
            language: The programming language.
            
        Returns:
            A list of category names.
        """
        if language not in self.prompts_by_language:
            return []
        
        categories = set()
        for prompt in self.prompts_by_language[language]:
            categories.add(prompt["category"])
        
        return list(categories)
    
    def get_subcategories(self, language: str, category: str) -> List[str]:
        """Get all available subcategories for a language and category.
        
        Args:
            language: The programming language.
            category: The vulnerability category.
            
        Returns:
            A list of subcategory names.
        """
        if language not in self.prompts_by_language:
            return []
        
        subcategories = set()
        for prompt in self.prompts_by_language[language]:
            if prompt["category"] == category:
                subcategories.add(prompt["subcategory"])
        
        return list(subcategories)
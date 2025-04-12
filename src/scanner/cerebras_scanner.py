import os
from typing import List, Dict, Any
from cerebras_cloud_sdk import CerebrasAPI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class CodeScanner:
    def __init__(self):
        """Initialize the scanner with Cerebras API client."""
        api_key = os.getenv("CEREBRAS_API_KEY")
        if not api_key:
            raise ValueError("CEREBRAS_API_KEY environment variable not found")
        
        self.client = CerebrasAPI(api_key=api_key)
        # Using Llama 2 70B model as it's available on Cerebras
        self.model = "meta-llama/Llama-2-70b-chat-hf"
        
    async def analyze_code(self, code: str, category: str) -> Dict[str, Any]:
        """
        Analyze a piece of code for security issues in a specific category.
        
        Args:
            code (str): The Python code to analyze
            category (str): The category of issues to look for (e.g., "sql_injection", "auth")
            
        Returns:
            Dict containing the analysis results
        """
        # Get the appropriate prompt template for this category
        prompt = self._get_prompt_template(category)
        
        # Format the prompt with the code
        formatted_prompt = prompt.format(code=code)
        
        try:
            # Call Cerebras API for inference
            response = await self.client.generate(
                model=self.model,
                prompt=formatted_prompt,
                max_tokens=1000,
                temperature=0.1,  # Low temperature for more focused analysis
                top_p=0.9,
                top_k=50,
                stop=["```"]  # Stop when code block ends
            )
            
            # Parse and return the response
            return self._parse_response(response.text if hasattr(response, 'text') else response)
            
        except Exception as e:
            return {
                "error": str(e),
                "category": category,
                "issues": []
            }
    
    def _get_prompt_template(self, category: str) -> str:
        """Get the appropriate prompt template for a category."""
        # TODO: Load these from a configuration file
        templates = {
            "sql_injection": """You are a security expert analyzing Python code for SQL injection vulnerabilities.
            
            Analyze this code and identify any potential SQL injection risks:
            
            ```python
            {code}
            ```
            
            List any SQL injection vulnerabilities found, explaining:
            1. Where the vulnerability is
            2. Why it's dangerous
            3. How to fix it
            
            Format your response in a clear, structured way.""",
            
            "auth": """You are a security expert analyzing Python code for authentication and credential security issues.
            
            Analyze this code and identify any authentication-related security issues:
            
            ```python
            {code}
            ```
            
            List any authentication vulnerabilities found, explaining:
            1. Where the vulnerability is
            2. Why it's dangerous
            3. How to fix it
            
            Format your response in a clear, structured way.""",
            
            # Add more templates for other categories...
        }
        
        return templates.get(category, "")
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse the LLM response into a structured format."""
        # TODO: Implement proper parsing based on the response format
        # For now, return a simple dict
        return {
            "raw_response": response,
            "issues": []  # We'll parse this properly later
        } 
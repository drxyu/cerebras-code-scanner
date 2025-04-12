#!/usr/bin/env python3
import os
import sys
import json
import yaml
import glob
import fnmatch
import logging
import argparse
import dotenv
import requests
from huggingface_hub import InferenceClient

# Load environment variables from .env file
dotenv.load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config(config_file='config.yaml'):
    """Load configuration from a YAML file."""
    try:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Config file '{config_file}' not found.")
        return {}
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def load_scanignore(directory):
    """
    Load patterns from .scanignore file in the same directory as the script.
    
    Returns:
        list: List of patterns to ignore
    """
    # Get the directory where the script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    scanignore_path = os.path.join(script_dir, '.scanignore')
    patterns = []
    
    try:
        if os.path.exists(scanignore_path):
            with open(scanignore_path, 'r') as file:
                for line in file:
                    # Strip whitespace and skip empty lines and comments
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
            logger.info(f"Loaded {len(patterns)} patterns from .scanignore (global setting)")
        else:
            logger.info("No .scanignore file found in script directory. Using default exclusions.")
    except Exception as e:
        logger.error(f"Error reading .scanignore: {e}")
    
    return patterns

def initialize_client():
    """
    Initialize a HuggingFace client using the API key from environment variables.
    
    Returns:
        str: The API key for HuggingFace
    """
    # Try to get the API key from environment variables
    api_key = os.environ.get("HF_API_KEY")
    
    # If not found in environment variables, try to load from configuration
    if not api_key:
        try:
            with open(os.path.expanduser("~/.cerebras/config.yaml"), "r") as f:
                config = yaml.safe_load(f)
                api_key = config.get("api_key")
        except (FileNotFoundError, yaml.YAMLError):
            pass
    
    if not api_key:
        logger.error("No HuggingFace API key found in environment variables or configuration file")
        sys.exit(1)
    
    return api_key

def load_prompt_repository(repo_file='prompts_repository.json'):
    """
    Load the prompt repository from a JSON file.
    
    Args:
        repo_file (str): Path to the prompt repository JSON file
        
    Returns:
        dict: The prompt repository
    """
    try:
        with open(repo_file, 'r') as file:
            repository = json.load(file)
            logger.info(f"Loaded prompt repository (version {repository.get('metadata', {}).get('version', 'unknown')})")
            return repository
    except FileNotFoundError:
        logger.warning(f"Prompt repository file '{repo_file}' not found. Using built-in prompts.")
        # Return a minimal built-in repository for backward compatibility
        return {
            "metadata": {
                "version": "built-in",
                "description": "Built-in prompts for backward compatibility"
            },
            "categories": {
                "python": {
                    "security": [
                        {
                            "id": "security-general",
                            "name": "General Security Analysis",
                            "prompt_template": """
                            Analyze the following Python code for security vulnerabilities,
                            focusing on:
                            1. SQL injection vulnerabilities
                            2. Command injection vulnerabilities
                            3. Path traversal issues
                            4. Authentication and authorization flaws
                            5. Improper error handling and information leakage
                            6. Hardcoded secrets
                            7. Insecure use of cryptographic functions
                            
                            For each issue found, explain the vulnerability and suggest a fix.
                            """,
                            "output_format": "markdown"
                        }
                    ],
                    "performance": [
                        {
                            "id": "performance-general",
                            "name": "General Performance Analysis",
                            "prompt_template": """
                            Analyze the following Python code for performance issues,
                            focusing on:
                            1. Inefficient algorithms or data structures
                            2. Repeated computations that could be cached
                            3. Unnecessary resource usage
                            4. Database query inefficiencies
                            5. Memory leaks or excessive memory usage
                            6. Threading or concurrency issues
                            
                            For each issue found, explain the performance problem and suggest an optimization.
                            """,
                            "output_format": "markdown"
                        }
                    ]
                },
                "sql": {
                    "security": [
                        {
                            "id": "sql-security-general",
                            "name": "General SQL Security Analysis",
                            "prompt_template": """
                            Analyze the following SQL code for security vulnerabilities,
                            focusing on:
                            1. SQL injection vulnerabilities
                            2. Privilege escalation risks
                            3. Insecure data access patterns
                            4. Improper access controls
                            5. Data exposure risks
                            6. Unsafe dynamic SQL
                            7. Improper error handling
                            
                            For each issue found, explain the vulnerability and suggest a fix.
                            """,
                            "output_format": "markdown"
                        }
                    ],
                    "performance": [
                        {
                            "id": "sql-performance-general",
                            "name": "General SQL Performance Analysis",
                            "prompt_template": """
                            Analyze the following SQL code for performance issues,
                            focusing on:
                            1. Inefficient queries (lack of proper indexing hints)
                            2. Suboptimal join techniques
                            3. Expensive operations (full table scans, cartesian products)
                            4. Missing indexes or constraints
                            5. Improper use of temporary tables or views
                            6. Redundant operations
                            7. Potential execution bottlenecks
                            
                            For each issue found, explain the performance problem and suggest an optimization.
                            """,
                            "output_format": "markdown"
                        },
                        {
                            "id": "sql-maintainability-general",
                            "name": "General SQL Maintainability Analysis",
                            "prompt_template": """
                            Analyze the following SQL code for maintainability issues,
                            focusing on:
                            1. Missing or inadequate comments
                            2. Inconsistent naming conventions
                            3. Overly complex queries
                            4. Hard-coded values
                            5. Duplicated code logic
                            6. Poor error handling
                            7. Inadequate schema organization
                            
                            For each issue found, explain the maintainability concern and suggest an improvement.
                            """,
                            "output_format": "markdown"
                        }
                    ]
                }
            },
            "prompt_generation": {
                "scanner_template": {
                    "security": "You are an expert code security auditor. Analyze the following {language} code carefully for security issues, focusing on {subcategory}.\n\n{prompt_template}\n\nCODE TO ANALYZE:\n```{language}\n{code_snippet}\n```",
                    "performance": "You are an expert {language} performance engineer. Analyze the following code for performance optimizations, focusing on {subcategory}.\n\n{prompt_template}\n\nCODE TO ANALYZE:\n```{language}\n{code_snippet}\n```",
                    "maintainability": "You are an expert {language} code reviewer. Analyze the following code for maintainability issues, focusing on {subcategory}.\n\n{prompt_template}\n\nCODE TO ANALYZE:\n```{language}\n{code_snippet}\n```"
                }
            }
        }
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON in prompt repository: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading prompt repository: {e}")
        return None

def get_formatted_prompt(repository, language, category, subcategory_id, code_snippet):
    """
    Generate a formatted prompt for the Cerebras API using the repository.
    
    Args:
        repository (dict): The prompt repository
        language (str): The programming language (e.g., 'python', 'sql')
        category (str): The category (e.g., 'security', 'performance')
        subcategory_id (str): The ID of the subcategory
        code_snippet (str): The code to analyze
        
    Returns:
        str: The formatted prompt
    """
    try:
        # Find the subcategory in the repository
        subcategory_entry = None
        for entry in repository["categories"][language][category]:
            if entry["id"] == subcategory_id:
                subcategory_entry = entry
                break
        
        if not subcategory_entry:
            logger.error(f"Subcategory {subcategory_id} not found in repository")
            return None
        
        # Get the template for the category
        template = repository["prompt_generation"]["scanner_template"][category]
        
        # Format the prompt
        prompt = template.format(
            language=language,
            subcategory=subcategory_entry["name"],
            prompt_template=subcategory_entry["prompt_template"],
            code_snippet=code_snippet
        )
        
        return prompt
    except KeyError as e:
        logger.error(f"Key error while formatting prompt: {e}")
        return None
    except Exception as e:
        logger.error(f"Error formatting prompt: {e}")
        return None

def get_batch_formatted_prompt(repository, language, category, subcategory_ids, code_snippet):
    """
    Generate a combined prompt for multiple subcategories to reduce API calls.
    
    Args:
        repository (dict): The prompt repository
        language (str): The programming language (e.g., 'python', 'sql')
        category (str): The category (e.g., 'security', 'performance')
        subcategory_ids (list): List of subcategory IDs to include in the batch
        code_snippet (str): The code to analyze
        
    Returns:
        tuple: (formatted_prompt, subcategory_details) where subcategory_details is a list of 
               dictionaries with 'id' and 'name' keys
    """
    try:
        if not subcategory_ids:
            return None, []
            
        subcategory_details = []
        subcategory_prompts = []
        
        # Get details for each subcategory
        for subcategory_id in subcategory_ids:
            subcategory_entry = None
            for entry in repository["categories"][language][category]:
                if entry["id"] == subcategory_id:
                    subcategory_entry = entry
                    break
            
            if not subcategory_entry:
                logger.warning(f"Subcategory {subcategory_id} not found in repository")
                continue
                
            subcategory_details.append({
                'id': subcategory_id,
                'name': subcategory_entry["name"]
            })
            subcategory_prompts.append(f"**{subcategory_entry['name']}**:\n{subcategory_entry['prompt_template']}")
        
        if not subcategory_details:
            return None, []
            
        # Create a combined prompt for all subcategories
        combined_template = f"""You are an expert {language} code analyzer specializing in {category} analysis.
        
Analyze the following code for {category} issues, addressing EACH of these specific areas:

{chr(10).join(subcategory_prompts)}

For each area, provide a separate section in your response with a clear heading matching the area name.
If an area has no issues, explicitly state that no issues were found for that area.

DO NOT skip any areas. Ensure you address all areas listed above.

CODE TO ANALYZE:
```{language}
{code_snippet}
```"""
        
        return combined_template, subcategory_details
    except KeyError as e:
        logger.error(f"Key error while formatting batch prompt: {e}")
        return None, []
    except Exception as e:
        logger.error(f"Error formatting batch prompt: {e}")
        return None, []

def analyze_with_cerebras(prompt, model=None):
    """
    Send a prompt to the HuggingFace Inference API.
    
    Args:
        prompt (str): The prompt to send
        model (str): Unused parameter, kept for compatibility
        
    Returns:
        dict: The API response
    """
    try:
        # Hard-coded model name as specified
        model_name = "meta-llama/Llama-3.3-70B-Instruct"
        api_key = initialize_client()
        
        # Initialize the client with the token
        client = InferenceClient(token=api_key)
        
        logger.info(f"Sending request to HuggingFace Inference API using {model_name} model")
        
        # Send the request to the HuggingFace API
        response = client.text_generation(
            f"You are an expert code analyzer specializing in security, performance, and code quality.\n\n{prompt}",
            model=model_name,
            max_new_tokens=2048,
            temperature=0.1,
            top_p=0.95,
        )
        
        # Create a response object with the same structure as expected by the rest of the code
        class MockResponse:
            def __init__(self, response_text):
                self.choices = [MockChoice(response_text)]
        
        class MockChoice:
            def __init__(self, text):
                self.message = MockMessage(text)
        
        class MockMessage:
            def __init__(self, content):
                self.content = content
        
        # Return the mock response
        return MockResponse(response)
        
    except Exception as e:
        logger.error(f"Error analyzing code with HuggingFace: {e}")
        return None

def should_scan_file(file_path):
    """
    Determine if a file should be scanned based on its extension.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        tuple: (should_scan, language) where should_scan is a boolean and language is 'python', 'sql', or None
    """
    # Check if file exists
    if not os.path.isfile(file_path):
        return False, None
    
    # Get the extension
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()
    
    # Check if it's a supported extension
    if ext == '.py':
        return True, 'python'
    elif ext in ['.sql', '.pgsql', '.tsql', '.plsql']:
        return True, 'sql'
    
    return False, None

def should_ignore_path(path, ignore_patterns):
    """
    Check if a path should be ignored based on patterns.
    
    Args:
        path (str): The path to check
        ignore_patterns (list): List of glob patterns to ignore
        
    Returns:
        bool: True if the path should be ignored, False otherwise
    """
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def split_into_batches(items, max_batch_size=3):
    """
    Split a list into smaller batches.
    
    Args:
        items (list): The list to split
        max_batch_size (int): Maximum size of each batch
        
    Returns:
        list: List of batches, where each batch is a list of items
    """
    return [items[i:i + max_batch_size] for i in range(0, len(items), max_batch_size)]

def scan_file(file_path, repository=None, categories=None, subcategories=None, legacy_mode=False):
    """
    Scan a single file for issues.
    
    Args:
        file_path (str): Path to the file to scan
        repository (dict): The prompt repository
        categories (list): List of categories to scan
        subcategories (list): List of subcategories to scan
        legacy_mode (bool): Use legacy mode
        
    Returns:
        dict: The scan result
    """
    try:
        # Determine the language
        should_scan, language = should_scan_file(file_path)
        if not should_scan or not language:
            logger.warning(f"Skipping {file_path} (unsupported file type)")
            return None
        
        # Read the file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None
        
        # Skip empty files
        if not content.strip():
            logger.warning(f"Skipping {file_path} (empty file)")
            return None
        
        # Prepare the result object
        result = {
            "file_path": file_path,
            "language": language,
            "analyses": []
        }
        
        # If using legacy mode, use predefined categories
        if legacy_mode:
            categories = ["security", "performance"]
            subcategories = None
        
        # Get relevant prompts for this language
        language_prompts = get_prompts_for_language(repository, language, categories, subcategories)
        if not language_prompts:
            logger.warning(f"No prompts found for {language} with categories {categories}")
            return None
        
        # Sort prompts by category for consistent results
        language_prompts.sort(key=lambda x: (x.get("category", ""), x.get("subcategory", "")))
        
        # Group prompts into batches for efficient API usage
        prompt_batches = split_into_batches(language_prompts, max_batch_size=3)
        
        # Process each batch
        for batch_idx, batch in enumerate(prompt_batches):
            batch_categories = [p.get("subcategory", "unknown") for p in batch]
            logger.info(f"Processing batch {batch_idx+1}/{len(prompt_batches)} with {len(batch)} subcategories")
            
            # Generate the prompt for this batch
            batch_prompt = generate_prompt(file_path, content, language, batch)
            
            # Send the prompt to the API
            response = analyze_with_cerebras(batch_prompt)
            
            # Parse the response
            if response and hasattr(response, 'choices') and response.choices:
                response_text = response.choices[0].message.content
                
                # Parse the results for each prompt in the batch
                batch_analyses = parse_batch_response(response_text, batch)
                
                # Add to the overall results
                if batch_analyses:
                    result["analyses"].extend(batch_analyses)
        
        # Empty analyses means no issues found
        if not result["analyses"]:
            logger.info(f"No issues found in {file_path}")
        
        return result
    except Exception as e:
        logger.error(f"Error scanning file {file_path}: {e}")
        return None

def combine_file_contents(files_to_batch, language):
    """
    Combine the contents of multiple files with clear dividers for batch processing.
    
    Args:
        files_to_batch (list): List of file paths to combine
        language (str): The language of the files
        
    Returns:
        tuple: (combined_content, file_info) where file_info is a list of dicts with file details
    """
    combined_content = ""
    file_info = []
    total_chars = 0
    
    for idx, file_path in enumerate(files_to_batch):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            if not content.strip():
                logger.warning(f"File {file_path} is empty, skipping")
                continue
                
            file_marker = f"\n\n### FILE_{idx+1}: {os.path.basename(file_path)} ###\n\n"
            
            if idx > 0:  # Add divider before all files except the first
                combined_content += file_marker
            else:  # For the first file
                combined_content += file_marker.lstrip()
                
            combined_content += content
            total_chars += len(content)
            
            file_info.append({
                "file_path": file_path,
                "file_marker": f"FILE_{idx+1}",
                "language": language,
                "size_chars": len(content)
            })
            
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
    
    logger.info(f"Combined {len(file_info)} files with total size of {total_chars} characters (approx. {total_chars//4} tokens)")
    return combined_content, file_info

def extract_file_section(content, file_marker):
    """
    Extract the section of a specific file from a multi-file response.
    
    Args:
        content (str): The full response content
        file_marker (str): The marker for the file section to extract
        
    Returns:
        str: The extracted section, or None if not found
    """
    try:
        import re
        
        # Look for the file marker
        pattern = rf"(?:^|\n)#+\s*{file_marker}.*?(?=\n#+\s*FILE|\Z)"
        
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0).strip()
            
        # Try alternative pattern if the model didn't use the exact format
        alt_pattern = rf"(?:^|\n).*?{file_marker}.*?(?=\n.*?FILE|\Z)"
        match = re.search(alt_pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(0).strip()
            
        return None
    except Exception as e:
        logger.warning(f"Error extracting file section: {e}")
        return None

def estimate_tokens(text):
    """
    Estimate the number of tokens in a text.
    A rough estimate is 4 characters per token for English text.
    
    Args:
        text (str): The text to estimate tokens for
        
    Returns:
        int: Estimated number of tokens
    """
    return len(text) // 4

def get_optimal_batch_size(files, language, max_tokens=6000):
    """
    Determine the optimal number of files to batch together based on their size.
    
    Args:
        files (list): List of file paths
        language (str): The language of the files
        max_tokens (int): Maximum token limit for the API
        
    Returns:
        list: List of batches, where each batch is a list of file paths
    """
    # Reserve tokens for prompt template and response
    available_tokens = max_tokens - 2000  # Reserve 2000 tokens for prompt template and overhead
    
    batches = []
    current_batch = []
    current_token_count = 0
    
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            file_token_count = estimate_tokens(content)
            file_with_markers_token_count = file_token_count + 100  # Add overhead for file markers
            
            # If adding this file would exceed the token limit, start a new batch
            if current_batch and (current_token_count + file_with_markers_token_count > available_tokens):
                batches.append(current_batch)
                current_batch = [file_path]
                current_token_count = file_with_markers_token_count
            else:
                current_batch.append(file_path)
                current_token_count += file_with_markers_token_count
                
        except Exception as e:
            logger.error(f"Error estimating tokens for {file_path}: {e}")
            # Add as a single file batch to be safe
            batches.append([file_path])
    
    # Add the last batch if it's not empty
    if current_batch:
        batches.append(current_batch)
        
    logger.info(f"Split {len(files)} files into {len(batches)} optimized batches based on token estimates")
    return batches

def scan_directory(directory_path, repository=None, categories=None, subcategories=None, 
                  ignore_patterns=None, legacy_mode=False, files_per_batch=3, max_tokens=6000):
    """
    Scan a directory for issues.
    
    Args:
        directory_path (str): Path to the directory to scan
        repository (dict): The prompt repository
        categories (list): List of categories to scan
        subcategories (list): List of subcategories to scan
        ignore_patterns (list): List of glob patterns to ignore
        legacy_mode (bool): Use legacy mode
        files_per_batch (int): Number of files to process in a batch
        max_tokens (int): Maximum tokens per API call
        
    Returns:
        list: The scan results
    """
    if ignore_patterns is None:
        ignore_patterns = []
    
    # Try to load .scanignore file if it exists
    scanignore_patterns = load_scanignore(directory_path)
    if scanignore_patterns:
        ignore_patterns.extend(scanignore_patterns)
    
    results = []
    
    # Walk through the directory
    for root, dirs, files in os.walk(directory_path):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if not should_ignore_path(os.path.join(root, d), ignore_patterns)]
        
        # Process each file
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip if the file should be ignored
            if should_ignore_path(file_path, ignore_patterns):
                continue
            
            # Check if this is a file type we can scan
            should_scan, _ = should_scan_file(file_path)
            if not should_scan:
                continue
            
            # Scan the file
            result = scan_file(
                file_path=file_path,
                repository=repository,
                categories=categories,
                subcategories=subcategories,
                legacy_mode=legacy_mode
            )
            
            if result:
                results.append(result)
    
    return results

def scan_file_batch(file_batch, language, repository, categories=None, subcategories=None, 
                   model="google/gemma-7b-it", legacy_mode=False):
    """
    Scan a batch of files of the same language.
    
    Args:
        file_batch (list): List of file paths to scan
        language (str): The language of the files (python or sql)
        repository (dict): The prompt repository
        categories (list, optional): List of categories to scan
        subcategories (list, optional): List of subcategory IDs to scan
        model (str): The model to use
        legacy_mode (bool): If True, use legacy scanning
        
    Returns:
        list: Results of the scan for each file
    """
    if not file_batch:
        return []
        
    # Combine file contents with clear dividers
    combined_content, file_info = combine_file_contents(file_batch, language)
    
    if not combined_content or not file_info:
        logger.warning("No valid content to analyze in the batch")
        return []
    
    batch_results = []
    
    # Default to all categories if none specified
    if not categories:
        categories = list(repository["prompt_generation"]["scanner_template"].keys())
    
    # Log what we're about to process
    logger.info(f"Processing {len(file_info)} {language} files with categories: {categories}")
    for file_data in file_info:
        logger.info(f"  - {file_data['file_path']} (approx. {file_data['size_chars']//4} tokens)")
    
    # Process each category for the batch of files
    for category in categories:
        if category not in repository["categories"][language]:
            logger.warning(f"Category {category} not available for {language}")
            continue
        
        # Get the subcategories to scan
        available_subcategories = [entry["id"] for entry in repository["categories"][language][category]]
        selected_subcategories = subcategories if subcategories else available_subcategories
        
        # Intersect with available subcategories
        selected_subcategories = [sc for sc in selected_subcategories if sc in available_subcategories]
        
        if not selected_subcategories:
            logger.warning(f"No valid subcategories found for {language}/{category}")
            continue
        
        # Split subcategories into smaller batches to avoid token limits
        subcategory_batches = split_into_batches(selected_subcategories, max_batch_size=3)
        logger.info(f"Scanning batch of {len(file_info)} {language} files for {category} with {len(selected_subcategories)} subcategories in {len(subcategory_batches)} API calls")
        
        for batch_idx, subcategory_batch in enumerate(subcategory_batches):
            logger.info(f"Processing subcategory batch {batch_idx+1}/{len(subcategory_batches)} with {len(subcategory_batch)} subcategories: {subcategory_batch}")
            
            # Create a multi-file batch prompt
            batch_prompt = f"""You are an expert {language} code analyzer specializing in {category} analysis.

Analyze the following code files for {category} issues. Each file is marked with a clear FILE_X header.
Treat each file separately and provide analysis for EACH file with clear file markers in your response.

For each file, address these specific areas:
"""
            
            # Add subcategory prompts
            subcategory_details = []
            for subcategory_id in subcategory_batch:
                subcategory_entry = None
                for entry in repository["categories"][language][category]:
                    if entry["id"] == subcategory_id:
                        subcategory_entry = entry
                        break
                
                if not subcategory_entry:
                    continue
                    
                subcategory_details.append({
                    'id': subcategory_id,
                    'name': subcategory_entry["name"]
                })
                batch_prompt += f"\n- **{subcategory_entry['name']}**:\n{subcategory_entry['prompt_template']}\n"
            
            if not subcategory_details:
                logger.warning(f"No subcategory details found for batch {batch_idx+1}")
                continue
                
            batch_prompt += """
For each file and each area above:
1. Start with a clear header identifying the file (e.g., "## FILE_1: filename.py")
2. Then for each area, provide a section with findings
3. If an area has no issues for a file, explicitly state that no issues were found

CODE FILES TO ANALYZE:
"""
            batch_prompt += combined_content
            
            logger.info(f"Sending API request with prompt of {len(batch_prompt)} characters (~{len(batch_prompt)//4} tokens)")
            
            # Send to Cerebras (one API call for multiple files and multiple subcategories)
            response = analyze_with_cerebras(batch_prompt, model)
            if not response:
                logger.error(f"No response received from API for batch {batch_idx+1}")
                continue
                
            # Process the response
            content = response.choices[0].message.content
            logger.info(f"Received response of {len(content)} characters (~{len(content)//4} tokens)")
            
            # Extract results for each file
            files_processed = 0
            for file_data in file_info:
                file_path = file_data["file_path"]
                file_marker = file_data["file_marker"]
                
                # Extract the section for this file
                file_section = extract_file_section(content, file_marker)
                
                if not file_section:
                    logger.warning(f"Could not extract results for {file_path} from the batch response")
                    continue
                
                logger.info(f"Extracted {len(file_section)} characters for {file_path}")
                files_processed += 1
                
                # Create or update the result for this file
                file_result = next((r for r in batch_results if r["file_path"] == file_path), None)
                
                if not file_result:
                    file_result = {
                        "file_path": file_path,
                        "language": language,
                        "analyses": []
                    }
                    batch_results.append(file_result)
                    logger.info(f"Added new result entry for {file_path}")
                
                # Add analyses for each subcategory
                for subcategory in subcategory_details:
                    subcategory_id = subcategory['id']
                    subcategory_name = subcategory['name']
                    
                    analysis = {
                        "category": category,
                        "subcategory": subcategory_name,
                        "subcategory_id": subcategory_id,
                        "content": file_section  # Store the file-specific section
                    }
                    file_result["analyses"].append(analysis)
                    logger.info(f"Added analysis for {file_path}: {category}/{subcategory_name}")
            
            logger.info(f"Processed {files_processed} files from batch {batch_idx+1}")
    
    logger.info(f"Batch processing complete. Found results for {len(batch_results)} files.")
    return batch_results

def format_results_markdown(results):
    """
    Format scan results as a Markdown document.
    
    Args:
        results (list): Results of the scan
        
    Returns:
        str: Markdown formatted results
    """
    if not results:
        return "# Scan Results\n\nNo results found."
    
    markdown = "# Code Scan Results\n\n"
    
    for file_result in results:
        file_path = file_result["file_path"]
        language = file_result["language"].capitalize()
        
        markdown += f"## {os.path.basename(file_path)}\n"
        markdown += f"**File:** {file_path}  \n"
        markdown += f"**Language:** {language}\n\n"
        
        # Group analyses by category
        analyses_by_category = {}
        for analysis in file_result["analyses"]:
            category = analysis["category"]
            if category not in analyses_by_category:
                analyses_by_category[category] = []
            analyses_by_category[category].append(analysis)
        
        # Add each category section
        for category, analyses in analyses_by_category.items():
            markdown += f"### {category.capitalize()} Analysis\n\n"
            
            # Track which batched responses we've already processed
            processed_contents = set()
            
            for analysis in analyses:
                subcategory = analysis["subcategory"]
                subcategory_id = analysis["subcategory_id"]
                content = analysis["content"]
                
                # If this content has already been processed (from a batch), skip it
                content_hash = hash(content)
                if content_hash in processed_contents:
                    continue
                    
                processed_contents.add(content_hash)
                
                # For batched responses, try to extract the relevant section
                extracted_content = extract_subcategory_section(content, subcategory)
                
                # If we can't extract a specific section (legacy mode or single-subcategory response)
                # or if the extracted content is empty, use the full content
                if not extracted_content:
                    markdown += f"#### {subcategory}\n\n"
                    markdown += f"{content}\n\n"
                    markdown += "---\n\n"
                else:
                    # For each analysis that shares this content, extract and add its section
                    for shared_analysis in [a for a in analyses if hash(a["content"]) == content_hash]:
                        shared_subcategory = shared_analysis["subcategory"]
                        section_content = extract_subcategory_section(content, shared_subcategory)
                        
                        if section_content:
                            markdown += f"#### {shared_subcategory}\n\n"
                            markdown += f"{section_content}\n\n"
                            markdown += "---\n\n"
    
    return markdown

def extract_subcategory_section(content, subcategory_name):
    """
    Extract a specific subcategory section from a batched response.
    
    Args:
        content (str): The full batched response content
        subcategory_name (str): The name of the subcategory to extract
        
    Returns:
        str: The extracted section, or None if not found
    """
    try:
        # Look for headings that match the subcategory name (with some flexibility)
        import re
        
        # Clean up the subcategory name for regex matching
        clean_name = re.sub(r'[^\w\s]', '.?', subcategory_name)
        pattern = rf"(?:^|\n)#+\s*{clean_name}.*?(?=\n#+\s|\Z)"
        
        # Try to find the section
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            section = match.group(0).strip()
            
            # Remove the heading itself
            section_content = re.sub(rf"^#+\s*{clean_name}.*?\n", "", section, 1, re.IGNORECASE)
            return section_content.strip()
            
        # Try alternative patterns if needed
        alternative_patterns = [
            # Bold text as heading
            rf"(?:^|\n)\*\*{clean_name}\*\*.*?(?=\n\*\*|\Z)",
            # Subcategory name followed by colon
            rf"(?:^|\n){clean_name}:.*?(?=\n\w+:|\Z)"
        ]
        
        for pattern in alternative_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                section = match.group(0).strip()
                return section
                
        return None
    except Exception as e:
        logger.warning(f"Error extracting subcategory section: {e}")
        return None

def save_results(results, output_file):
    """
    Save scan results to a file.
    
    Args:
        results (list): Results of the scan
        output_file (str): Path to the output file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Format results as Markdown
        markdown = format_results_markdown(results)
        
        # Write to file
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(markdown)
        
        logger.info(f"Results saved to {output_file}")
        return True
    except Exception as e:
        logger.error(f"Error saving results: {e}")
        return False

def get_prompts_for_language(repository, language, categories=None, subcategories=None):
    """
    Get relevant prompts for a given language based on categories and subcategories.
    
    Args:
        repository (dict): The prompt repository
        language (str): The language to get prompts for
        categories (list): List of categories to include
        subcategories (list): List of subcategories to include
        
    Returns:
        list: List of prompt configurations
    """
    if not repository or not repository.get("categories") or not repository["categories"].get(language):
        logger.warning(f"No prompts found for language: {language}")
        return []
    
    # Default to all categories if none specified
    if not categories:
        categories = list(repository["categories"][language].keys())
    
    prompts = []
    
    # Gather prompts for each category
    for category in categories:
        if category not in repository["categories"][language]:
            logger.warning(f"Category '{category}' not available for {language}")
            continue
        
        # Get all subcategories for this category
        available_subcategories = repository["categories"][language][category]
        
        # Filter by requested subcategories if specified
        if subcategories:
            filtered_subcategories = [sc for sc in available_subcategories 
                                     if sc["id"] in subcategories]
        else:
            filtered_subcategories = available_subcategories
        
        # Add prompts for each subcategory
        for subcategory in filtered_subcategories:
            prompts.append({
                "category": category,
                "subcategory": subcategory["name"],
                "subcategory_id": subcategory["id"],
                "prompt_template": subcategory.get("prompt_template"),
                "output_format": subcategory.get("output_format"),
                "example_fix": subcategory.get("example_fix")
            })
    
    return prompts

def generate_prompt(file_path, content, language, prompts):
    """
    Generate a formatted prompt for a batch of subcategories.
    
    Args:
        file_path (str): Path to the file
        content (str): Content of the file
        language (str): The language (python or sql)
        prompts (list): List of prompt configurations
        
    Returns:
        str: The formatted prompt
    """
    file_name = os.path.basename(file_path)
    
    # Create the intro section
    intro = f"""Analyze the following {language.upper()} code from '{file_name}'.

CODE:
```{language}
{content}
```

REQUESTED ANALYSIS: 
"""
    
    # Add each analysis request
    for i, prompt_config in enumerate(prompts):
        category = prompt_config["category"]
        subcategory = prompt_config["subcategory"]
        prompt_template = prompt_config.get("prompt_template", f"Analyze the code for {subcategory} issues.")
        
        intro += f"\n{i+1}. {category.upper()}: {subcategory} - {prompt_template}\n"
    
    # Instructions for the output format
    intro += "\nPlease provide separate analysis sections for each requested analysis, formatted as follows:\n"
    
    for i, prompt_config in enumerate(prompts):
        intro += f"\n## ANALYSIS {i+1}: {prompt_config['category'].upper()}: {prompt_config['subcategory']}\n"
        
        if prompt_config.get("output_format"):
            intro += f"Output format: {prompt_config['output_format']}\n"
        
        if prompt_config.get("example_fix"):
            intro += f"Example fix: {prompt_config['example_fix']}\n"
    
    return intro

def parse_batch_response(response_text, prompts):
    """
    Parse the response from a batch analysis.
    
    Args:
        response_text (str): The response text from the API
        prompts (list): The list of prompt configurations
        
    Returns:
        list: List of parsed analyses
    """
    analyses = []
    
    # Check if we have a response
    if not response_text:
        return []
    
    # Try to split the response by analysis sections
    analysis_sections = []
    
    # Look for section headers
    for i, prompt in enumerate(prompts):
        section_header = f"## ANALYSIS {i+1}: {prompt['category'].upper()}: {prompt['subcategory']}"
        alt_section_header = f"## ANALYSIS {i+1}:"
        
        # Find the section in the response
        section_start = response_text.find(section_header)
        if section_start == -1:
            section_start = response_text.find(alt_section_header)
            if section_start == -1:
                continue
        
        # Find the start of the next section or the end of text
        next_section_idx = i + 1
        if next_section_idx < len(prompts):
            next_section_header = f"## ANALYSIS {next_section_idx+1}: {prompts[next_section_idx]['category'].upper()}: {prompts[next_section_idx]['subcategory']}"
            alt_next_section_header = f"## ANALYSIS {next_section_idx+1}:"
            
            section_end = response_text.find(next_section_header)
            if section_end == -1:
                section_end = response_text.find(alt_next_section_header)
                if section_end == -1:
                    section_end = len(response_text)
        else:
            section_end = len(response_text)
        
        # Extract the section content
        section_content = response_text[section_start:section_end].strip()
        
        # Add to analyses
        analyses.append({
            "category": prompt["category"],
            "subcategory": prompt["subcategory"],
            "subcategory_id": prompt["subcategory_id"],
            "content": section_content
        })
    
    # If we couldn't parse sections, use the entire response for each prompt
    if not analyses:
        for prompt in prompts:
            analyses.append({
                "category": prompt["category"],
                "subcategory": prompt["subcategory"],
                "subcategory_id": prompt["subcategory_id"],
                "content": response_text
            })
    
    return analyses

def format_results(result, output_file):
    """
    Format the results as a markdown file.
    
    Args:
        result (dict): The scan results
        output_file (str): Path to the output file
        
    Returns:
        None
    """
    if not result:
        logger.warning("No results to format")
        return
    
    # Create a markdown string
    markdown = "# Code Scan Results\n\n"
    
    # Add summary
    file_path = result.get("file_path", "Unknown file")
    language = result.get("language", "Unknown language")
    analysis_count = len(result.get("analyses", []))
    
    markdown += f"## Summary\n\n"
    markdown += f"- **File:** {file_path}\n"
    markdown += f"- **Language:** {language.capitalize()}\n"
    markdown += f"- **Analysis Count:** {analysis_count}\n\n"
    
    # Add each analysis
    markdown += "## Analysis Results\n\n"
    
    for i, analysis in enumerate(result.get("analyses", [])):
        category = analysis.get("category", "Unknown")
        subcategory = analysis.get("subcategory", "Unknown")
        content = analysis.get("content", "No content")
        
        markdown += f"### {i+1}. {category.capitalize()}: {subcategory}\n\n"
        markdown += f"{content}\n\n"
        markdown += "---\n\n"
    
    # Write to file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error writing results to {output_file}: {e}")

def main():
    """Main function to handle command line arguments and run the scanner."""
    parser = argparse.ArgumentParser(description="Scan code for security and performance issues using AI.")
    parser.add_argument("path", help="Path to the file or directory to scan")
    parser.add_argument("-o", "--output", help="Path to the output file (default: output.md)", default="output.md")
    parser.add_argument("-r", "--repository", help="Path to the prompts repository file", 
                      default="prompts_repository.json")
    parser.add_argument("-c", "--categories", help="Categories to scan (comma-separated, default: all)",
                      default="")
    parser.add_argument("-s", "--subcategories", help="Subcategories to scan (comma-separated, default: all)",
                      default="")
    parser.add_argument("-v", "--verbose", help="Enable verbose logging", action="store_true")
    
    args = parser.parse_args()
    
    # Set up logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    else:
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Set up the prompts repository
    repository_path = args.repository
    repository = load_prompt_repository(repository_path)
    
    # Parse categories and subcategories
    categories = args.categories.split(",") if args.categories else []
    subcategories = args.subcategories.split(",") if args.subcategories else []
    
    # Clean up empty strings from split
    categories = [c for c in categories if c]
    subcategories = [s for s in subcategories if s]
    
    if os.path.isfile(args.path):
        # Single file scanning
        result = scan_file(
            file_path=args.path,
            repository=repository,
            categories=categories,
            subcategories=subcategories
        )
        format_results(result, args.output)
        return 0
    elif os.path.isdir(args.path):
        # Directory scanning
        result = scan_directory(
            directory_path=args.path,
            repository=repository,
            categories=categories,
            subcategories=subcategories
        )
        format_results(result, args.output)
        return 0
    else:
        logger.error(f"Path not found: {args.path}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 
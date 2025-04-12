#!/usr/bin/env python3
import os
import sys
import json
import yaml
import glob
import fnmatch
import logging
import argparse
from cerebras.cloud.sdk import Cerebras

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

def load_scanignore():
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

def initialize_cerebras_client():
    """Initialize the Cerebras client with API key from environment or config."""
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if not api_key:
        config = load_config()
        api_key = config.get('cerebras', {}).get('api_key')
    
    if not api_key:
        logger.error("No Cerebras API key found in environment or config.")
        logger.error("Please set the CEREBRAS_API_KEY environment variable or add it to config.yaml")
        raise ValueError("No Cerebras API key found")
    
    return Cerebras(api_key=api_key)

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
                        }
                    ]
                }
            },
            "prompt_generation": {
                "scanner_template": {
                    "security": "You are an expert code security auditor. Analyze the following {language} code carefully for security issues, focusing on {subcategory}.\n\n{prompt_template}\n\nCODE TO ANALYZE:\n```{language}\n{code_snippet}\n```",
                    "performance": "You are an expert {language} performance engineer. Analyze the following code for performance optimizations, focusing on {subcategory}.\n\n{prompt_template}\n\nCODE TO ANALYZE:\n```{language}\n{code_snippet}\n```"
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

def analyze_with_cerebras(prompt, model="llama-4-scout-17b-16e-instruct"):
    """
    Send a prompt to the Cerebras API and get the response.
    
    Args:
        prompt (str): The prompt to send
        model (str): The Cerebras model to use
        
    Returns:
        dict: The API response
    """
    try:
        client = initialize_cerebras_client()
        
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code analyzer specializing in security, performance, and code quality."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model=model,
        )
        
        return chat_completion
    except Exception as e:
        logger.error(f"Error analyzing code: {e}")
        return None

def should_ignore_path(path, ignore_patterns):
    """
    Check if a path should be ignored based on patterns.
    
    Args:
        path (str): Path to check
        ignore_patterns (list): List of glob patterns to ignore
        
    Returns:
        bool: True if the path should be ignored, False otherwise
    """
    if not ignore_patterns:
        return False
    
    # Normalize path for consistent pattern matching
    normalized_path = os.path.normpath(path)
    
    for pattern in ignore_patterns:
        if fnmatch.fnmatch(normalized_path, pattern) or \
           fnmatch.fnmatch(os.path.basename(normalized_path), pattern):
            return True
    
    return False

def should_scan_file(file_path, config=None, ignore_patterns=None):
    """
    Determine if a file should be scanned based on its extension and ignore patterns.
    
    Args:
        file_path (str): Path to the file
        config (dict, optional): Configuration settings
        ignore_patterns (list, optional): List of glob patterns to ignore
        
    Returns:
        tuple: (should_scan, language) where language is 'python', 'sql', or None
    """
    if should_ignore_path(file_path, ignore_patterns):
        logger.debug(f"Skipping {file_path} (matches ignore pattern)")
        return False, None
    
    # Check file extension
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == '.py':
        return True, 'python'
    elif ext in ['.sql', '.pgsql', '.tsql', '.plsql']:
        return True, 'sql'
    
    return False, None

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

def scan_file(file_path, repository, categories=None, subcategories=None, model="llama-4-scout-17b-16e-instruct", legacy_mode=False):
    """
    Scan a single file for issues.
    
    Args:
        file_path (str): Path to the file to scan
        repository (dict): The prompt repository
        categories (list, optional): List of categories to scan (e.g., ['security', 'performance'])
        subcategories (list, optional): List of subcategory IDs to scan
        model (str): The Cerebras model to use
        legacy_mode (bool): If True, use legacy scanning (just security and performance)
        
    Returns:
        dict: Results of the scan
    """
    try:
        # Determine the language
        _, language = should_scan_file(file_path, ignore_patterns=[])
        if not language:
            logger.warning(f"Could not determine language for {file_path}")
            return None
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as file:
            code_snippet = file.read()
        
        if not code_snippet:
            logger.warning(f"File {file_path} is empty")
            return None
        
        results = {
            "file_path": file_path,
            "language": language,
            "analyses": []
        }
        
        # Handle legacy mode (pre-expandable system)
        if legacy_mode:
            # Legacy mode only uses security and performance categories with general subcategories
            security_prompt = get_formatted_prompt(
                repository, language, "security", f"{language}-security-general" if language == "sql" else "security-general", code_snippet
            )
            if security_prompt:
                response = analyze_with_cerebras(security_prompt, model)
                if response:
                    results["analyses"].append({
                        "category": "security",
                        "subcategory": "Security Analysis",
                        "subcategory_id": "security-general",
                        "content": response.choices[0].message.content
                    })
            
            performance_prompt = get_formatted_prompt(
                repository, language, "performance", f"{language}-performance-general" if language == "sql" else "performance-general", code_snippet
            )
            if performance_prompt:
                response = analyze_with_cerebras(performance_prompt, model)
                if response:
                    results["analyses"].append({
                        "category": "performance",
                        "subcategory": "Performance Analysis",
                        "subcategory_id": "performance-general",
                        "content": response.choices[0].message.content
                    })
            
            return results
        
        # Enhanced mode with expandable prompts
        
        # Default to all categories if none specified
        if not categories:
            categories = list(repository["prompt_generation"]["scanner_template"].keys())
        
        # Scan for each selected category (group subcategories to reduce API calls)
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
                continue
            
            # Split subcategories into smaller batches to avoid token limits
            subcategory_batches = split_into_batches(selected_subcategories, max_batch_size=3)
            logger.info(f"Scanning {file_path} for {language}/{category} with {len(selected_subcategories)} subcategories in {len(subcategory_batches)} batches...")
            
            for batch_idx, subcategory_batch in enumerate(subcategory_batches):
                logger.info(f"Processing batch {batch_idx+1}/{len(subcategory_batches)} with {len(subcategory_batch)} subcategories")
                
                # Get the batch formatted prompt
                batch_prompt, subcategory_details = get_batch_formatted_prompt(
                    repository, language, category, subcategory_batch, code_snippet
                )
                
                if not batch_prompt or not subcategory_details:
                    continue
                
                # Send to Cerebras (one API call for all subcategories in this batch)
                response = analyze_with_cerebras(batch_prompt, model)
                if not response:
                    continue
                    
                # Process the combined response
                content = response.choices[0].message.content
                    
                # Add entry for each subcategory in the batch
                for subcategory in subcategory_details:
                    subcategory_id = subcategory['id']
                    subcategory_name = subcategory['name']
                    
                    # Add to results (full response for now, we'll parse it in the output formatter)
                    analysis = {
                        "category": category,
                        "subcategory": subcategory_name,
                        "subcategory_id": subcategory_id,
                        "content": content  # Store full response for each subcategory
                    }
                    results["analyses"].append(analysis)
        
        return results
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

def scan_directory(directory_path, repository, categories=None, subcategories=None, 
                  ignore_patterns=None, model="llama-4-scout-17b-16e-instruct", legacy_mode=False, 
                  files_per_batch=3, max_tokens=6000):
    """
    Recursively scan a directory for Python and SQL files.
    
    Args:
        directory_path (str): Path to the directory to scan
        repository (dict): The prompt repository
        categories (list, optional): List of categories to scan
        subcategories (list, optional): List of subcategory IDs to scan
        ignore_patterns (list, optional): List of glob patterns to ignore
        model (str): The Cerebras model to use
        legacy_mode (bool): If True, use legacy scanning
        files_per_batch (int): Number of files to process in a single batch (used if token-based batching is disabled)
        max_tokens (int): Maximum token limit for the API (default: 6000)
        
    Returns:
        list: Results of the scan
    """
    if ignore_patterns is None:
        ignore_patterns = load_scanignore()
    
    logger.info(f"Scanning directory: {directory_path}")
    logger.info(f"Loaded {len(ignore_patterns)} patterns from .scanignore (global setting)")
    
    # Find all Python and SQL files in the directory
    logger.info(f"Recursively searching for Python and SQL files in {directory_path}...")
    
    all_files = []
    for ext in ['.py', '.sql', '.pgsql', '.tsql', '.plsql']:
        pattern = os.path.join(directory_path, f"**/*{ext}")
        all_files.extend(glob.glob(pattern, recursive=True))
    
    # Filter out ignored files
    files_to_scan = []
    skipped_files = []
    
    for file_path in all_files:
        should_scan, _ = should_scan_file(file_path, ignore_patterns=ignore_patterns)
        if should_scan:
            files_to_scan.append(file_path)
        else:
            skipped_files.append(file_path)
    
    logger.info(f"Scan summary: Found {len(all_files)} Python/SQL files, scanning {len(files_to_scan)}, skipped {len(skipped_files)}")
    
    if len(files_to_scan) == 0:
        if len(all_files) > 0:
            logger.warning(f"All {len(all_files)} files were skipped due to filters")
            logger.info("To see which files were skipped, check the .scanignore file or increase log verbosity")
        else:
            logger.warning(f"No Python or SQL files found in {directory_path}")
        return []
    
    # Group files by language for batch processing
    python_files = [f for f in files_to_scan if f.lower().endswith('.py')]
    sql_files = [f for f in files_to_scan if any(f.lower().endswith(ext) for ext in ['.sql', '.pgsql', '.tsql', '.plsql'])]
    
    # Use token-based batching for optimal API usage
    python_batches = get_optimal_batch_size(python_files, 'python', max_tokens)
    sql_batches = get_optimal_batch_size(sql_files, 'sql', max_tokens)
    
    logger.info(f"Grouped files into {len(python_batches)} Python batches and {len(sql_batches)} SQL batches")
    
    # Log detailed information about batches
    for i, batch in enumerate(python_batches):
        logger.info(f"Python batch {i+1}: {len(batch)} files ({', '.join([os.path.basename(f) for f in batch])})")
    for i, batch in enumerate(sql_batches):
        logger.info(f"SQL batch {i+1}: {len(batch)} files ({', '.join([os.path.basename(f) for f in batch])})")
    
    results = []
    
    # Process Python file batches
    if python_batches:
        for batch_idx, batch in enumerate(python_batches):
            logger.info(f"Processing Python batch {batch_idx+1}/{len(python_batches)} with {len(batch)} files")
            batch_results = scan_file_batch(batch, 'python', repository, categories, subcategories, model, legacy_mode)
            if batch_results:
                results.extend(batch_results)
    
    # Process SQL file batches
    if sql_batches:
        for batch_idx, batch in enumerate(sql_batches):
            logger.info(f"Processing SQL batch {batch_idx+1}/{len(sql_batches)} with {len(batch)} files")
            batch_results = scan_file_batch(batch, 'sql', repository, categories, subcategories, model, legacy_mode)
            if batch_results:
                results.extend(batch_results)
    
    return results

def scan_file_batch(file_batch, language, repository, categories=None, subcategories=None, 
                   model="llama-4-scout-17b-16e-instruct", legacy_mode=False):
    """
    Scan a batch of files of the same language.
    
    Args:
        file_batch (list): List of file paths to scan
        language (str): The language of the files (python or sql)
        repository (dict): The prompt repository
        categories (list, optional): List of categories to scan
        subcategories (list, optional): List of subcategory IDs to scan
        model (str): The Cerebras model to use
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
            continue
        
        # Split subcategories into smaller batches to avoid token limits
        subcategory_batches = split_into_batches(selected_subcategories, max_batch_size=3)
        logger.info(f"Scanning batch of {len(file_info)} {language} files for {category} with {len(selected_subcategories)} subcategories in {len(subcategory_batches)} API calls")
        
        for batch_idx, subcategory_batch in enumerate(subcategory_batches):
            logger.info(f"Processing subcategory batch {batch_idx+1}/{len(subcategory_batches)} with {len(subcategory_batch)} subcategories")
            
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
                continue
                
            batch_prompt += """
For each file and each area above:
1. Start with a clear header identifying the file (e.g., "## FILE_1: filename.py")
2. Then for each area, provide a section with findings
3. If an area has no issues for a file, explicitly state that no issues were found

CODE FILES TO ANALYZE:
"""
            batch_prompt += combined_content
            
            # Send to Cerebras (one API call for multiple files and multiple subcategories)
            response = analyze_with_cerebras(batch_prompt, model)
            if not response:
                continue
                
            # Process the response
            content = response.choices[0].message.content
            
            # Extract results for each file
            for file_data in file_info:
                file_path = file_data["file_path"]
                file_marker = file_data["file_marker"]
                
                # Extract the section for this file
                file_section = extract_file_section(content, file_marker)
                
                if not file_section:
                    logger.warning(f"Could not extract results for {file_path} from the batch response")
                    continue
                
                # Create or update the result for this file
                file_result = next((r for r in batch_results if r["file_path"] == file_path), None)
                
                if not file_result:
                    file_result = {
                        "file_path": file_path,
                        "language": language,
                        "analyses": []
                    }
                    batch_results.append(file_result)
                
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

def main():
    parser = argparse.ArgumentParser(description="AI-Powered Python/SQL Code Scanner using Cerebras")
    parser.add_argument("path", help="Path to file or directory to scan")
    parser.add_argument("-o", "--output", default="scan_results.md", help="Output file path")
    parser.add_argument("-m", "--model", default="llama-4-scout-17b-16e-instruct", help="Cerebras model to use")
    parser.add_argument("-r", "--repository", default="prompts_repository.json", help="Path to prompt repository JSON file")
    parser.add_argument("-c", "--categories", nargs='+', choices=["security", "performance", "maintainability"], 
                      help="Categories to scan (default: all)")
    parser.add_argument("-s", "--subcategories", nargs='+', help="Specific subcategories to scan (default: all)")
    parser.add_argument("-l", "--legacy", action="store_true", help="Use legacy mode (basic security and performance checks only)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("-b", "--batch-size", type=int, default=3, help="Number of files to process in a single batch (if token-based batching is disabled)")
    parser.add_argument("-t", "--max-tokens", type=int, default=6000, help="Maximum token limit for API calls (default: 6000)")
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Load the prompt repository
    repository = load_prompt_repository(args.repository)
    if not repository:
        logger.error("Failed to load prompt repository.")
        return 1
    
    # Check if path exists
    if not os.path.exists(args.path):
        logger.error(f"Path does not exist: {args.path}")
        return 1
    
    # Scan the path
    if os.path.isdir(args.path):
        results = scan_directory(
            args.path, repository, args.categories, args.subcategories, 
            model=args.model, legacy_mode=args.legacy, 
            files_per_batch=args.batch_size,
            max_tokens=args.max_tokens
        )
    else:
        result = scan_file(
            args.path, repository, args.categories, args.subcategories, 
            model=args.model, legacy_mode=args.legacy
        )
        results = [result] if result else []
    
    # Save the results
    if results:
        save_results(results, args.output)
        logger.info(f"Scan completed successfully. Results saved to {args.output}")
    else:
        logger.warning("No results found.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
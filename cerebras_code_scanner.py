import os
import sys
import yaml
import glob
import fnmatch
import logging
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

def analyze_code_security(code_snippet, model="llama-4-scout-17b-16e-instruct"):
    """
    Analyze a Python code snippet for security vulnerabilities using Cerebras AI.
    
    Args:
        code_snippet (str): The Python code to analyze
        model (str): The Cerebras model to use
        
    Returns:
        dict: The AI's analysis of security vulnerabilities
    """
    client = initialize_cerebras_client()
    
    prompt = f"""
    You are a Python security expert. Analyze the following code for security vulnerabilities,
    focusing on:
    1. SQL injection vulnerabilities
    2. Command injection vulnerabilities
    3. Path traversal issues
    4. Authentication and authorization flaws
    5. Improper error handling and information leakage
    6. Hardcoded secrets
    7. Insecure use of cryptographic functions
    
    For each issue found, explain the vulnerability and suggest a fix.
    
    CODE TO ANALYZE:
    ```python
    {code_snippet}
    ```
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a Python security expert specializing in application security vulnerabilities."
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

def analyze_code_performance(code_snippet, model="llama-4-scout-17b-16e-instruct"):
    """
    Analyze a Python code snippet for performance issues using Cerebras AI.
    
    Args:
        code_snippet (str): The Python code to analyze
        model (str): The Cerebras model to use
        
    Returns:
        dict: The AI's analysis of performance issues
    """
    client = initialize_cerebras_client()
    
    prompt = f"""
    You are a Python performance optimization expert. Analyze the following code for performance issues,
    focusing on:
    1. Inefficient algorithms or data structures
    2. Repeated computations that could be cached
    3. Unnecessary resource usage
    4. Database query inefficiencies
    5. Memory leaks or excessive memory usage
    6. Threading or concurrency issues
    
    For each issue found, explain the performance problem and suggest an optimization.
    
    CODE TO ANALYZE:
    ```python
    {code_snippet}
    ```
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a Python performance optimization expert."
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

def analyze_sql_security(sql_code, model="llama-4-scout-17b-16e-instruct"):
    """
    Analyze SQL code for security vulnerabilities using Cerebras AI.
    
    Args:
        sql_code (str): The SQL code to analyze
        model (str): The Cerebras model to use
        
    Returns:
        dict: The AI's analysis of security vulnerabilities
    """
    client = initialize_cerebras_client()
    
    prompt = f"""
    You are a SQL security expert. Analyze the following SQL code for security vulnerabilities,
    focusing on:
    1. SQL injection vulnerabilities
    2. Privilege escalation risks
    3. Insecure data access patterns
    4. Improper access controls
    5. Data exposure risks
    6. Unsafe dynamic SQL
    7. Improper error handling
    
    For each issue found, explain the vulnerability and suggest a fix.
    
    SQL CODE TO ANALYZE:
    ```sql
    {sql_code}
    ```
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a SQL security expert specializing in database security vulnerabilities."
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
        logger.error(f"Error analyzing SQL code: {e}")
        return None

def analyze_sql_performance(sql_code, model="llama-4-scout-17b-16e-instruct"):
    """
    Analyze SQL code for performance issues using Cerebras AI.
    
    Args:
        sql_code (str): The SQL code to analyze
        model (str): The Cerebras model to use
        
    Returns:
        dict: The AI's analysis of performance issues
    """
    client = initialize_cerebras_client()
    
    prompt = f"""
    You are a SQL performance optimization expert. Analyze the following SQL code for performance issues,
    focusing on:
    1. Inefficient queries (lack of proper indexing hints)
    2. Suboptimal join techniques
    3. Expensive operations (full table scans, cartesian products)
    4. Missing indexes or constraints
    5. Improper use of temporary tables or views
    6. Redundant operations
    7. Potential execution bottlenecks
    
    For each issue found, explain the performance problem and suggest an optimization.
    
    SQL CODE TO ANALYZE:
    ```sql
    {sql_code}
    ```
    """
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a SQL performance optimization expert."
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
        logger.error(f"Error analyzing SQL code: {e}")
        return None

def should_ignore_path(path, ignore_patterns):
    """
    Check if a path should be ignored based on .scanignore patterns.
    
    Args:
        path (str): The path to check
        ignore_patterns (list): Patterns from .scanignore
        
    Returns:
        bool: True if the path should be ignored
    """
    # Normalize the path to prevent path traversal
    path = os.path.normpath(path)
    path_parts = path.split(os.sep)
    
    for pattern in ignore_patterns:
        # Handle directory-specific patterns (ends with /)
        if pattern.endswith('/'):
            dir_pattern = pattern[:-1]
            for i in range(len(path_parts)):
                if fnmatch.fnmatch(path_parts[i], dir_pattern):
                    return True
        # Handle file patterns with path components
        elif '/' in pattern:
            pattern_parts = pattern.split('/')
            if len(pattern_parts) <= len(path_parts):
                match = True
                for i, part in enumerate(pattern_parts):
                    if not fnmatch.fnmatch(path_parts[i], part):
                        match = False
                        break
                if match:
                    return True
        # Handle simple file patterns
        else:
            if fnmatch.fnmatch(os.path.basename(path), pattern):
                return True
    
    return False

def should_scan_file(file_path, config=None, ignore_patterns=None):
    """
    Check if a file should be scanned based on configuration and .scanignore.
    
    Args:
        file_path (str): Path to the file
        config (dict): Scanner configuration
        ignore_patterns (list): Patterns from .scanignore
        
    Returns:
        bool: True if the file should be scanned, False otherwise
    """
    # Normalize path to prevent path traversal attacks
    file_path = os.path.abspath(os.path.normpath(file_path))
    
    # Check if file is a supported type
    if not (file_path.endswith('.py') or file_path.endswith('.sql')):
        return False
        
    if config is None:
        config = load_config()
    
    # Debug file path
    filename = os.path.basename(file_path)
    
    # OVERRIDE: Force-include specific directories regardless of .scanignore
    # Adjust this list based on directories you always want to scan
    force_include_dirs = [
        "azure-sql-db-python-rest-api"
    ]
    
    for include_dir in force_include_dirs:
        if include_dir in file_path:
            logger.info(f"Force-including {file_path} (overrides .scanignore)")
            return True
    
    # Log info about this file only if it's in specific directories we're debugging
    if "azure-sql-db-python-rest-api" in file_path:
        logger.info(f"Evaluating file for scanning: {file_path}")
    
    # Check against .scanignore patterns first - silently skip matches
    if ignore_patterns and should_ignore_path(file_path, ignore_patterns):
        if "azure-sql-db-python-rest-api" in file_path:
            logger.info(f"File {filename} matched a pattern in .scanignore")
        return False
    
    # Check file size - added back with a higher reasonable limit
    max_file_size = config.get('scanning', {}).get('max_file_size', 100000)  # 100KB default
    if os.path.getsize(file_path) > max_file_size:
        logger.info(f"Skipping {file_path}: File exceeds maximum size of {max_file_size} bytes")
        return False
    
    # Check excluded directories from config
    excluded_dirs = config.get('scanning', {}).get('excluded_directories', [])
    for excluded_dir in excluded_dirs:
        if excluded_dir in file_path:
            logger.info(f"Skipping {file_path}: In excluded directory {excluded_dir}")
            return False
    
    # Check excluded file patterns from config
    excluded_files = config.get('scanning', {}).get('excluded_files', [])
    for pattern in excluded_files:
        if glob.fnmatch.fnmatch(os.path.basename(file_path), pattern):
            logger.info(f"Skipping {file_path}: Matches excluded pattern {pattern}")
            return False
    
    return True

def scan_directory(directory_path, model="llama-4-scout-17b-16e-instruct"):
    """
    Scan all Python and SQL files in a directory and its subdirectories.
    
    Args:
        directory_path (str): Path to the directory to scan
        model (str): The Cerebras model to use
        
    Returns:
        dict: Results of the scan organized by file
    """
    config = load_config()
    results = {}
    files_found = 0
    files_skipped = 0
    files_scanned = 0
    
    # Load patterns from .scanignore
    ignore_patterns = load_scanignore()
    
    # Get all Python and SQL files recursively
    logger.info(f"Recursively searching for Python and SQL files in {directory_path}...")
    for root, _, files in os.walk(directory_path):
        for file in files:
            is_python = file.endswith('.py')
            is_sql = file.endswith('.sql')
            
            if is_python or is_sql:
                files_found += 1
                file_path = os.path.join(root, file)
                
                if should_scan_file(file_path, config, ignore_patterns):
                    files_scanned += 1
                    logger.info(f"Scanning {file_path}...")
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code = f.read()
                        
                        if is_python:
                            security_analysis = analyze_code_security(code, model)
                            performance_analysis = analyze_code_performance(code, model)
                        elif is_sql:
                            security_analysis = analyze_sql_security(code, model)
                            performance_analysis = analyze_sql_performance(code, model)
                        
                        results[file_path] = {
                            'security': security_analysis.choices[0].message.content if security_analysis else "Failed to analyze security issues",
                            'performance': performance_analysis.choices[0].message.content if performance_analysis else "Failed to analyze performance issues"
                        }
                    except Exception as e:
                        logger.error(f"Error processing {file_path}: {e}")
                        results[file_path] = {
                            'security': f"Error: {str(e)}",
                            'performance': f"Error: {str(e)}"
                        }
                else:
                    files_skipped += 1
    
    logger.info(f"Scan summary: Found {files_found} Python/SQL files, scanned {files_scanned}, skipped {files_skipped}")
    
    if files_found == 0:
        logger.warning(f"No Python (.py) or SQL (.sql) files found in {directory_path}")
    elif files_skipped == files_found:
        logger.warning(f"All {files_found} files were skipped due to filters")
        logger.info("To see which files were skipped, check the .scanignore file or increase log verbosity")
    
    return results

def display_results(results):
    """
    Display the results of the scan in an organized manner.
    
    Args:
        results (dict): Results of the scan organized by file
    """
    for file_path, analyses in results.items():
        print(f"\n{'=' * 80}")
        print(f"FILE: {file_path}")
        print(f"{'=' * 80}\n")
        
        print(f"\n{'-' * 50}")
        print("SECURITY ANALYSIS:")
        print(f"{'-' * 50}\n")
        print(analyses['security'])
        
        print(f"\n{'-' * 50}")
        print("PERFORMANCE ANALYSIS:")
        print(f"{'-' * 50}\n")
        print(analyses['performance'])

def save_results_to_file(results, output_file="scan_results.md"):
    """
    Save the results of the scan to a file.
    
    Args:
        results (dict): Results of the scan organized by file
        output_file (str): Path to the output file
    """
    # Sanitize output file path
    output_file = os.path.abspath(os.path.normpath(output_file))
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Code Scan Results\n\n")
            
            for file_path, analyses in results.items():
                f.write(f"## {file_path}\n\n")
                
                f.write("### Security Analysis\n\n")
                f.write(analyses['security'])
                f.write("\n\n")
                
                f.write("### Performance Analysis\n\n")
                f.write(analyses['performance'])
                f.write("\n\n")
                
                f.write("---\n\n")
        
        logger.info(f"Results saved to {output_file}")
    except Exception as e:
        logger.error(f"Error saving results to {output_file}: {e}")

def main():
    """Main function to scan Python files for security and performance issues."""
    if len(sys.argv) < 2:
        logger.error("Usage: python cerebras_code_scanner.py <path_to_directory_or_file>")
        return
    
    try:
        # Normalize path to prevent path traversal attacks
        path = os.path.abspath(os.path.normpath(sys.argv[1]))
        
        config = load_config()
        model = config.get('cerebras', {}).get('model', "llama-4-scout-17b-16e-instruct")
        
        if os.path.isdir(path):
            logger.info(f"Scanning directory: {path}")
            results = scan_directory(path, model)
            display_results(results)
            
            # Save results to file if configured
            if config.get('output', {}).get('save_to_file', False):
                output_file = config.get('output', {}).get('output_file', "scan_results.md")
                save_results_to_file(results, output_file)
        else:
            # Maintain backward compatibility for single file scanning
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    code = file.read()
            except Exception as e:
                logger.error(f"Error reading file {path}: {e}")
                return
            
            print(f"\n{'=' * 50}")
            print(f"SECURITY ANALYSIS FOR: {path}")
            print(f"{'=' * 50}\n")
            security_analysis = analyze_code_security(code, model)
            if security_analysis:
                print(security_analysis.choices[0].message.content)
            
            print(f"\n{'=' * 50}")
            print(f"PERFORMANCE ANALYSIS FOR: {path}")
            print(f"{'=' * 50}\n")
            performance_analysis = analyze_code_performance(code, model)
            if performance_analysis:
                print(performance_analysis.choices[0].message.content)
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
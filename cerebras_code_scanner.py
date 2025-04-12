import os
import sys
import yaml
import glob
from cerebras.cloud.sdk import Cerebras

def load_config(config_file='config.yaml'):
    """Load configuration from a YAML file."""
    try:
        with open(config_file, 'r') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Config file '{config_file}' not found.")
        return {}
    except Exception as e:
        print(f"Error loading config: {e}")
        return {}

def initialize_cerebras_client():
    """Initialize the Cerebras client with API key from environment or config."""
    api_key = os.environ.get("CEREBRAS_API_KEY")
    if not api_key:
        config = load_config()
        api_key = config.get('cerebras', {}).get('api_key')
    
    if not api_key:
        print("Warning: No Cerebras API key found in environment or config.")
        print("Please set the CEREBRAS_API_KEY environment variable or add it to config.yaml")
    
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
        print(f"Error analyzing code: {e}")
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
        print(f"Error analyzing code: {e}")
        return None

def should_scan_file(file_path, config=None):
    """
    Check if a file should be scanned based on configuration.
    
    Args:
        file_path (str): Path to the file
        config (dict): Scanner configuration
        
    Returns:
        bool: True if the file should be scanned, False otherwise
    """
    if not file_path.endswith('.py'):
        return False
        
    if config is None:
        config = load_config()
    
    # Check excluded directories
    excluded_dirs = config.get('scanning', {}).get('excluded_directories', [])
    for excluded_dir in excluded_dirs:
        if excluded_dir in file_path:
            print(f"Skipping {file_path}: In excluded directory {excluded_dir}")
            return False
    
    # Check excluded file patterns
    excluded_files = config.get('scanning', {}).get('excluded_files', [])
    for pattern in excluded_files:
        if glob.fnmatch.fnmatch(os.path.basename(file_path), pattern):
            print(f"Skipping {file_path}: Matches excluded pattern {pattern}")
            return False
    
    return True

def scan_directory(directory_path, model="llama-4-scout-17b-16e-instruct"):
    """
    Scan all Python files in a directory and its subdirectories.
    
    Args:
        directory_path (str): Path to the directory to scan
        model (str): The Cerebras model to use
        
    Returns:
        dict: Results of the scan organized by file
    """
    config = load_config()
    results = {}
    
    # Get all Python files recursively
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                
                if should_scan_file(file_path, config):
                    print(f"Scanning {file_path}...")
                    
                    try:
                        with open(file_path, 'r') as f:
                            code = f.read()
                            
                        security_analysis = analyze_code_security(code, model)
                        performance_analysis = analyze_code_performance(code, model)
                        
                        results[file_path] = {
                            'security': security_analysis.choices[0].message.content if security_analysis else "Failed to analyze security issues",
                            'performance': performance_analysis.choices[0].message.content if performance_analysis else "Failed to analyze performance issues"
                        }
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
                        results[file_path] = {
                            'security': f"Error: {str(e)}",
                            'performance': f"Error: {str(e)}"
                        }
    
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
    with open(output_file, 'w') as f:
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
    
    print(f"Results saved to {output_file}")

def main():
    """Main function to scan Python files for security and performance issues."""
    if len(sys.argv) < 2:
        print("Usage: python cerebras_code_scanner.py <path_to_directory_or_file>")
        return
    
    path = sys.argv[1]
    config = load_config()
    model = config.get('cerebras', {}).get('model', "llama-4-scout-17b-16e-instruct")
    
    if os.path.isdir(path):
        print(f"Scanning directory: {path}")
        results = scan_directory(path, model)
        display_results(results)
        
        # Save results to file if configured
        if config.get('output', {}).get('save_to_file', False):
            output_file = config.get('output', {}).get('output_file', "scan_results.md")
            save_results_to_file(results, output_file)
    else:
        # Maintain backward compatibility for single file scanning
        try:
            with open(path, 'r') as file:
                code = file.read()
        except Exception as e:
            print(f"Error reading file {path}: {e}")
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

if __name__ == "__main__":
    main() 
# AI-Powered Code Security & Performance Scanner

An AI-powered security and performance scanner for Python and SQL codebases, leveraging Cerebras and Llama 4 to identify application-level vulnerabilities and performance issues.

## Features

- **Python Security Analysis**: Detects common security vulnerabilities in Python code.
  - SQL injection vulnerabilities
  - Command injection vulnerabilities
  - Path traversal issues
  - Authentication and authorization flaws
  - Improper error handling and information leakage
  - Hardcoded secrets
  - Insecure use of cryptographic functions

- **Python Performance Analysis**: Identifies performance bottlenecks and inefficiencies.
  - Inefficient algorithms or data structures
  - Repeated computations that could be cached
  - Unnecessary resource usage
  - Database query inefficiencies
  - Memory leaks or excessive memory usage
  - Threading or concurrency issues

- **SQL Security Analysis**: Identifies security issues in SQL code.
  - SQL injection vulnerabilities
  - Privilege escalation risks
  - Insecure data access patterns
  - Improper access controls
  - Data exposure risks
  - Unsafe dynamic SQL
  - Improper error handling

- **SQL Performance Analysis**: Detects performance problems in SQL queries.
  - Inefficient queries (lack of proper indexing hints)
  - Suboptimal join techniques
  - Expensive operations (full table scans, cartesian products)
  - Missing indexes or constraints
  - Improper use of temporary tables or views
  - Redundant operations
  - Potential execution bottlenecks

## How It Works

### Architecture & Workflow

The code scanner operates through a layered architecture:

1. **File Discovery Layer**: Recursively walks through directories to find Python and SQL files for analysis.
2. **Filtering Layer**: Applies configurable rules to exclude certain files and directories.
3. **Analysis Layer**: Sends code to Cerebras-hosted Llama 4 models for deep inspection.
4. **Reporting Layer**: Organizes and displays findings in a structured format.

### Analysis Mechanism

The tool leverages Large Language Models (LLMs) for code understanding:

1. **AI-Powered Analysis**: Rather than using rule-based pattern matching like traditional scanners, this tool utilizes Cerebras's high-performance AI infrastructure running Llama 4 models to semantically understand code.

2. **Specialized Prompts**: Each file is analyzed twice through carefully engineered prompts:
   - A security-focused prompt that instructs the model to identify vulnerabilities
   - A performance-focused prompt that seeks optimization opportunities

3. **Context-Aware Detection**: The LLM understands code context beyond simple pattern recognition, enabling it to:
   - Detect vulnerabilities in complex control flows
   - Understand security implications across function calls
   - Identify performance bottlenecks in algorithmic patterns
   - Recognize data structure inefficiencies

### Processing Flow

The scanning process follows these steps:

1. **Configuration Loading**: The scanner reads settings from `config.yaml` or environment variables.
2. **File Discovery**: When scanning a directory, the tool recursively identifies all Python and SQL files.
3. **Filtering**: Files are filtered based on exclusion rules (directories to skip, file patterns to ignore).
4. **Content Reading**: Each file's content is read into memory.
5. **Security Analysis**: Code is sent to Cerebras with a security-focused prompt.
6. **Performance Analysis**: Code is sent to Cerebras with a performance-focused prompt.
7. **Result Collection**: Findings from both analyses are collected and organized by file.
8. **Display & Output**: Results are presented in the terminal and optionally saved to a Markdown file.

### Cerebras Integration

The scanner utilizes Cerebras's advanced AI infrastructure:

1. **API Integration**: Communicates with Cerebras through their Cloud SDK.
2. **Model Selection**: Uses the specified Llama 4 model variant for inference.
3. **Prompt Engineering**: Leverages carefully structured prompts to guide the AI analysis.
4. **Response Processing**: Extracts and formats the AI's analysis for presentation.

This approach combines the contextual understanding of large language models with the speed and efficiency of Cerebras's specialized AI hardware, enabling deeper analysis than traditional static analyzers while maintaining reasonable performance.

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/drxyu/cerebras-code-scanner.git
   cd cerebras-code-scanner
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install --upgrade cerebras_cloud_sdk
   pip install pyyaml
   ```

4. Set your Cerebras API key:
   ```
   export CEREBRAS_API_KEY="your_api_key_here"
   ```
   Alternatively, update the `config.yaml` file with your API key.

## Usage

### Scan a Single File

```
python cerebras_code_scanner.py path/to/your/file.py
# or
python cerebras_code_scanner.py path/to/your/query.sql
```

### Scan an Entire Directory

The scanner can also analyze all Python and SQL files in a directory and its subdirectories:

```
python cerebras_code_scanner.py path/to/your/project/
```

This will:
- Recursively find all Python (.py) and SQL (.sql) files in the directory
- Skip files in excluded directories (configurable in config.yaml)
- Skip files that match excluded patterns (configurable in config.yaml)
- Skip files larger than the maximum size (configurable in config.yaml)
- Skip files that match patterns in `.scanignore` (global setting)
- Output results organized by file

### Using .scanignore

The scanner uses a `.scanignore` file located in the same directory as the script as a global setting. This file uses the same syntax as `.gitignore` to specify which files and directories to exclude from scanning, regardless of which directory is being scanned:

```
# Directories to ignore
venv/
node_modules/
__pycache__/

# File patterns to ignore
*.pyc
*.pyo
*.log

# Specific files 
config_local.py
test_data.py
```

## Configuration

The scanner can be configured using the `config.yaml` file:

- **cerebras**: Cerebras API configuration
  - **api_key**: Your Cerebras API key (better to use environment variable)
  - **model**: Default model to use for analysis

- **scanning**: Scanning configuration
  - **max_file_size**: Maximum file size to scan in bytes (default 100KB)
  - **excluded_directories**: Directories to exclude from scanning
  - **excluded_files**: File patterns to exclude from scanning

- **output**: Output configuration
  - **format**: Output format (text, json, markdown)
  - **save_to_file**: Whether to save the results to a file
  - **output_file**: File to save the results to

## File Exclusion Priority

When determining which files to scan, the scanner applies exclusion rules in the following order:

1. File extension check (only `.py` and `.sql` files are scanned)
2. Patterns from `.scanignore` (global setting)
3. File size limit from config.yaml
4. Excluded directories from config.yaml
5. Excluded file patterns from config.yaml

## Output

The scanner organizes results by file and for each file provides:
- Security analysis findings
- Performance analysis findings

Results can be displayed in the terminal and/or saved to a Markdown file.

## Requirements

- Python 3.8+
- cerebras-cloud-sdk
- pyyaml

## TEST CASES: 
1. Self.

Feedback: 
  docs/self_scan_improvement_1.txt	
  docs/self_scan_result_1.txt
  docs/self_scan_improvement_2.txt	
  docs/self_scan_result_2.txt

2. Azure sql api.
https://github.com/Azure-Samples/azure-sql-db-python-rest-api

Feedback:
  docs/azure-sql-db-python-rest-api.txt

3. Bookclub webapp.
https://github.com/ms4985/BookClubWebApp.git

Feedback:
  docs/BookClubWebApp.txt


## License

MIT

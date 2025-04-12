# AI-Powered Python Security & Performance Scanner

An AI-powered security and performance scanner for Python backend codebases, leveraging Cerebras and Llama 4 to identify application-level vulnerabilities and performance issues.

## Features

- **Security Analysis**: Detects common security vulnerabilities in Python code.
  - SQL injection vulnerabilities
  - Command injection vulnerabilities
  - Path traversal issues
  - Authentication and authorization flaws
  - Improper error handling and information leakage
  - Hardcoded secrets
  - Insecure use of cryptographic functions

- **Performance Analysis**: Identifies performance bottlenecks and inefficiencies.
  - Inefficient algorithms or data structures
  - Repeated computations that could be cached
  - Unnecessary resource usage
  - Database query inefficiencies
  - Memory leaks or excessive memory usage
  - Threading or concurrency issues

## How It Works

### Architecture & Workflow

The code scanner operates through a layered architecture:

1. **File Discovery Layer**: Recursively walks through directories to find Python files for analysis.
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
2. **File Discovery**: When scanning a directory, the tool recursively identifies all Python files.
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
   git clone https://github.com/yourusername/ai-code-scanner.git
   cd ai-code-scanner
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install cerebras-cloud-sdk pyyaml
   ```

4. Set your Cerebras API key:
   ```
   export CEREBRAS_API_KEY="your_api_key_here"
   ```
   Alternatively, update the `config.yaml` file with your API key.

## Usage

### Scan a Single File

```
python cerebras_code_scanner.py path/to/your/python_file.py
```

### Scan an Entire Directory

The scanner can also analyze all Python files in a directory and its subdirectories:

```
python cerebras_code_scanner.py path/to/your/project/
```

This will:
- Recursively find all Python files in the directory
- Skip files in excluded directories (configurable in config.yaml)
- Skip files that match excluded patterns (configurable in config.yaml)
- Output results organized by file

## Configuration

The scanner can be configured using the `config.yaml` file:

- **cerebras**: Cerebras API configuration
  - **api_key**: Your Cerebras API key (better to use environment variable)
  - **model**: Default model to use for analysis

- **scanning**: Scanning configuration
  - **excluded_directories**: Directories to exclude from scanning
  - **excluded_files**: File patterns to exclude from scanning

- **output**: Output configuration
  - **format**: Output format (text, json, markdown)
  - **save_to_file**: Whether to save the results to a file
  - **output_file**: File to save the results to

## Output

The scanner organizes results by file and for each file provides:
- Security analysis findings
- Performance analysis findings

Results can be displayed in the terminal and/or saved to a Markdown file.

## Requirements

- Python 3.8+
- cerebras-cloud-sdk
- pyyaml

## License

MIT
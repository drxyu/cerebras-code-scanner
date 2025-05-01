# AI-Powered Code Security & Performance Scanner

## Project Origin

This project was created during the [Cerebras Llama 4 Hackathon](https://lu.ma/eihdh2gd?tk=GfcyGK) on April 12, 2025.   

(Updated:  🏆 One of 5 prize winners! 🏆  `\m/_(>.<)_\m/` )

Inspired by Cerebras's performance and Llama 4's capabilities, this scanner leverages prompt engineering to extract code insights that traditional rule-based tools cannot detect, enabling deeper security and performance analysis.

---

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

- **Expandable Prompt System**: Customize and extend the scanner with your own checks.
  - External prompt repository in JSON format
  - Add new languages, categories, or subcategory checks
  - Focused scanning by category or specific issue type
  - Multi-round scanning for deeper analysis

- **Optimized API Usage**: Intelligent API call batching to avoid rate limits.
  - Combines multiple checks into batched requests
  - Automatically splits subcategories into optimal batch sizes
  - Reduces number of API calls by up to 70%
  - Minimizes "Too Many Requests" (429) errors
  - Extracts individual check results from batched responses

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

2. **Specialized Prompts**: Each file is analyzed through carefully engineered prompts:
   - Security-focused prompts that instruct the model to identify vulnerabilities
   - Performance-focused prompts that seek optimization opportunities
   - Maintainability prompts that identify code quality issues

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
   pip install huggingface_hub python-dotenv
   ```

4. Set your Cerebras API key:
   ```
   export CEREBRAS_API_KEY="your_api_key_here"
   ```
   Alternatively, update the `config.yaml` file with your API key.

## Usage

### Basic Scanning

#### Scan a Single File

```
python cerebras_code_scanner.py path/to/your/file.py -o results.md
```

#### Scan an Entire Directory

```
python cerebras_code_scanner.py path/to/your/project/ -o results.md
```

This will:
- Recursively find all Python (.py) and SQL (.sql) files in the directory
- Skip files matching patterns in `.scanignore` (global setting)
- Output results organized by file to the specified markdown file

### Advanced Features

The scanner supports a variety of options for customized analysis:

#### Scan with Specific Categories

```
# Scan for security issues only
python cerebras_code_scanner.py path/to/your/project/ -c security -o results.md

# Scan for performance and maintainability issues
python cerebras_code_scanner.py path/to/your/project/ -c performance,maintainability -o results.md
```

#### Scan for Specific Issues

```
# Check only for SQL injection and command injection
python cerebras_code_scanner.py path/to/your/project/ -s sql-injection,command-injection -o results.md

# Check specific performance issues
python cerebras_code_scanner.py path/to/your/project/ -s nested-loops,inefficient-data-structure -o results.md
```

#### Customizing Output

```
# Save results to a specific file
python cerebras_code_scanner.py path/to/your/project/ -o my_scan_results.md
```

#### Enable Verbose Logging

```
# Run with verbose logging for more details about the scanning process
python cerebras_code_scanner.py path/to/your/project/ -v -o results.md
```

#### Using a Custom Prompt Repository

```
# Use a different prompt repository
python cerebras_code_scanner.py path/to/your/project/ -r my_custom_prompts.json -o results.md
```

### Extending the Scanner

The expandable prompt system allows you to add your own checks:

1. Create or edit `prompts_repository.json`
2. Add new entries for specific issue types
3. Run the scanner with your custom checks

For detailed information on customization, see [PROMPT_SYSTEM.md](PROMPT_SYSTEM.md).

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

The scanner generates a comprehensive analysis in Markdown format, with results organized by:

1. **File**: Each scanned file has its own section.
2. **Category**: Each file's results are divided into Security and Performance categories.
3. **Analysis**: Detailed findings with explanations and recommendations.

Results are displayed in the terminal and optionally saved to a file (default: scan_results.md).

### API Usage Optimization

The scanner now uses an intelligent batching system to reduce API calls and avoid rate limits:

- **Combined Checks**: Instead of making a separate API call for each subcategory check, the scanner batches multiple checks into a single request.

- **Automatic Batch Sizing**: The scanner automatically determines optimal batch sizes to balance efficiency with response quality.

- **Smart Parsing**: Results from batched responses are intelligently parsed to extract findings for individual checks.

- **Reduced Rate Limiting**: By minimizing the number of API calls, you'll encounter fewer "Too Many Requests" (429) errors, especially when scanning large codebases.

- **Token-Based Multi-File Batching**: The scanner now intelligently combines multiple files into a single API call based on token count estimation, maximizing API efficiency while staying within token limits.

- **Optimal Token Usage**: Files are automatically grouped to use as much of the available token context as possible without exceeding limits.

This optimization is transparent - you don't need to configure anything differently. If you previously encountered rate limiting issues, try running your scan again with the latest version.

#### Advanced Token Control

For specific use cases, you can adjust the token limits:

```bash
# Set maximum token limit to 8000 (for models with larger context windows)
python cerebras_code_scanner.py path/to/your/project/ --max-tokens 8000
```

## Requirements

- Python 3.8+
- cerebras-cloud-sdk
- pyyaml

## TEST CASES: 

> **Disclaimer**: The repositories used for testing were randomly selected from Google search results. All copyrights belong to their original owners. If you are an owner of any referenced repository and wish to have it removed from this documentation, please contact us and we will promptly remove it.

1. Self.
    Feedback: 
    ```
      docs/self_scan_improvement_1.txt	
      docs/self_scan_result_1.txt
      docs/self_scan_improvement_2.txt	
      docs/self_scan_result_2.txt
    ```

2. Azure sql api.
https://github.com/Azure-Samples/azure-sql-db-python-rest-api
    Feedback:
    ```
      docs/azure-sql-db-python-rest-api.txt
    ```

3. Bookclub webapp.
https://github.com/ms4985/BookClubWebApp.git
    Feedback:
    ```
      docs/BookClubWebApp.txt
    ```


![Demo] (https://private-user-images.githubusercontent.com/3768015/439695732-fa8ce317-72cb-45ed-837c-34f01a29d1dd.mp4?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NDYxMjY4NzMsIm5iZiI6MTc0NjEyNjU3MywicGF0aCI6Ii8zNzY4MDE1LzQzOTY5NTczMi1mYThjZTMxNy03MmNiLTQ1ZWQtODM3Yy0zNGYwMWEyOWQxZGQubXA0P1gtQW16LUFsZ29yaXRobT1BV1M0LUhNQUMtU0hBMjU2JlgtQW16LUNyZWRlbnRpYWw9QUtJQVZDT0RZTFNBNTNQUUs0WkElMkYyMDI1MDUwMSUyRnVzLWVhc3QtMSUyRnMzJTJGYXdzNF9yZXF1ZXN0JlgtQW16LURhdGU9MjAyNTA1MDFUMTkwOTMzWiZYLUFtei1FeHBpcmVzPTMwMCZYLUFtei1TaWduYXR1cmU9NzJkMjQ1Yjk2YmVjMTgzZGI5ZWFiNzY3NDZjNjhhZTIxZjlmYWI5MDg1MzhhNWNlOTczOWY1NjJkNjlkYTYzNiZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QifQ.omQRH2B1t5wsvZloPbuHKETJJQ2BO6_y3oKOws-WXU4)
    

## TODO Next

1. **Performance Benchmarking**: Compare analysis quality and performance metrics among:
   - **Leading Proprietary Models**: OpenAI GPT-4, Anthropic Claude 3
   - **Leading Open Models**: Meta Llama 3, Mistral Large
   - **Code Analysis Services**: GitHub Copilot, Amazon CodeWhisperer

2. **Multi-Language Support**: Extend the platform to support additional languages:
   - **General-Purpose Languages**: Java, JavaScript/TypeScript, Go, Rust, C/C++
   - **Domain-Specific Languages**: Terraform, CloudFormation, Dockerfile
   - **System Configurations**: Kubernetes YAML, Nginx configs, SSH configs, Apache configs
   - **Build Scripts**: GitHub Actions, Jenkins, CircleCI

## Legal Disclaimer

### No Warranty and Limitation of Liability

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

### Use at Your Own Risk

The AI-Powered Code Security & Performance Scanner is a tool designed to assist in identifying potential code issues; however:

1. It does not guarantee the discovery of all vulnerabilities, performance issues, or code defects.
2. Results provided by the scanner are based on AI analysis and may include false positives or miss certain issues.
3. Users should independently verify all findings and exercise professional judgment when implementing suggested changes.
4. The scanner is not a substitute for thorough code reviews, security audits, or performance testing by qualified professionals.
5. The authors and contributors are not responsible for any damage, data loss, or security breaches resulting from the use of this tool or implementation of its suggestions.

### No Endorsement

The use of the AI-Powered Code Security & Performance Scanner to analyze any codebase does not constitute an endorsement, certification, or guarantee of the quality, security, or performance of the analyzed software by the scanner's creators, contributors, or associated entities.

### Third-Party Content

The scanner may reference or analyze third-party code, frameworks, or libraries. Such references do not constitute endorsement of those third parties, and all trademarks and copyrights remain the property of their respective owners.

## License

MIT

## Copyright

Copyright © 2025 [DrXyu](https://github.com/drxyu). All Rights Reserved.

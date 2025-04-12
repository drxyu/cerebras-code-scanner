# Expandable Prompt System for Cerebras Code Scanner

This document explains how to use and extend the AI-powered code scanner's prompt system, allowing you to customize and enhance the scanning capabilities.

## Overview

The scanner uses a flexible, modular prompt repository that organizes prompts by:

- **Language**: Python, SQL, etc.
- **Category**: Security, Performance, Maintainability, etc.
- **Subcategory**: Specific issue types (SQL Injection, Nested Loops, etc.)

This architecture makes it easy to add new scanning capabilities or modify existing ones without changing the core code.

## Repository Structure

The prompt repository is stored in `prompts_repository.json` with this structure:

```json
{
  "metadata": {
    "version": "1.0.0",
    "description": "Expandable prompt repository for Cerebras Code Scanner",
    "last_updated": "2025-04-12"
  },
  "categories": {
    "language": {
      "category": [
        {
          "id": "subcategory-id",
          "name": "Subcategory Name",
          "prompt_template": "The prompt text that describes what to look for...",
          "output_format": "markdown",
          "example_fix": "Example code demonstrating how to fix the issue"
        },
        // More subcategories...
      ],
      // More categories...
    },
    // More languages...
  },
  "prompt_generation": {
    "scanner_template": {
      "category": "Template for generating the final prompt, including placeholders"
    }
  }
}
```

## How to Use the Enhanced Scanner

The new scanner supports various command-line options for customized scans:

```bash
python cerebras_expanded_scanner.py /path/to/scan --categories security performance --subcategories sql-injection inefficient-data-structure
```

### Key Options:

- `path`: The file or directory to scan
- `-o, --output`: Output file path (default: scan_results.md)
- `-m, --model`: Cerebras model to use (default: llama-4-scout-17b-16e-instruct)
- `-r, --repository`: Path to the prompt repository (default: prompts_repository.json)
- `-c, --categories`: Categories to scan (security, performance, maintainability)
- `-s, --subcategories`: Specific subcategories to scan (ids from the repository)
- `-v, --verbose`: Enable verbose logging

## Adding New Prompts

To add a new prompt category or subcategory:

1. Open `prompts_repository.json`
2. Add your new entry to the appropriate section:

```json
{
  "id": "my-new-check",
  "name": "My New Check",
  "prompt_template": "Analyze the following code for my specific issue pattern...",
  "output_format": "markdown",
  "example_fix": "Example of how to fix the issue"
}
```

## Adding a New Language

To add a new language (e.g., JavaScript):

1. Add a new top-level key under "categories"
2. Define the categories and subcategories for that language

```json
"javascript": {
  "security": [
    {
      "id": "js-xss",
      "name": "Cross-Site Scripting (XSS)",
      "prompt_template": "Analyze the JavaScript code for XSS vulnerabilities...",
      "output_format": "markdown",
      "example_fix": "Example fix for XSS in JavaScript"
    }
  ]
}
```

## Multi-Round Scanning

The scanner supports multi-round analysis by defining different subcategories. For detailed analysis:

1. First run a scan for specific categories
2. Based on the results, run a focused scan on specific files or subcategories

```bash
# First round - basic security check
python cerebras_expanded_scanner.py /my/code --categories security

# Second round - focused performance scan on a specific file
python cerebras_expanded_scanner.py /my/code/specific_file.py --categories performance
```

## Example: Custom Security Check

To add a custom check for logging sensitive information:

1. Add to the repository:

```json
{
  "id": "sensitive-logging",
  "name": "Sensitive Information Logging",
  "prompt_template": "Check the code for instances where sensitive information (passwords, tokens, personal data) might be logged or printed to console. Identify any logging statements that could leak secrets or private data.",
  "output_format": "markdown",
  "example_fix": "Instead of: logger.info(f\"User authenticated with password {password}\")\nUse: logger.info(f\"User authenticated successfully\")"
}
```

2. Run the scanner with your new check:

```bash
python cerebras_expanded_scanner.py /path/to/code --subcategories sensitive-logging
```

## Advanced: Crafting Effective Prompts

For optimal results, consider these guidelines when creating prompts:

1. **Be specific**: Clearly identify the exact issue pattern you want to find
2. **Provide context**: Explain why it's a problem and what impact it has
3. **Include examples**: Show what a vulnerability looks like in code
4. **Request concrete fixes**: Ask for specific recommendations to fix the issue
5. **Standardize output**: Request consistent output format for easier processing

## Integrating with Development Workflows

The expandable prompt system can be integrated into CI/CD pipelines:

1. Create a custom repository with organization-specific checks
2. Run focused scans as part of pull request validation
3. Generate security reports during builds

For example in a GitHub Action:

```yaml
- name: Run Security Scan
  run: python cerebras_expanded_scanner.py ${{ github.workspace }} --categories security --output scan_results.md
```

## Extending the Scanner

The modular design allows for several types of extensions:

1. **New Prompt Categories**: Add entirely new scanning dimensions (e.g., "compliance" or "testability")
2. **Custom Output Formats**: Modify the formatter to output results in different formats (e.g., JSON, HTML)
3. **Integration with Other Tools**: Feed results to other security or quality tools 
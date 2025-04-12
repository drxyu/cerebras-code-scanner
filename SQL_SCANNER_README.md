# SQL Query Performance Scanner

A specialized tool that leverages Cerebras-hosted Llama 4 model to scan SQL queries for performance issues and suggest optimizations based on best practices.

## Overview

This tool is an extension of the Cerebras Code Scanner, specifically designed to analyze SQL queries for performance issues. It uses the Cerebras-hosted Llama 4 model to identify common SQL performance problems and provide recommendations for optimization.

## Features

- Scan SQL files for performance issues
- Identify common SQL anti-patterns
- Provide recommendations for query optimization
- Generate comprehensive Markdown reports

## Prerequisites

1. Cerebras API key (set in config.json)
2. Python 3.x
3. Required dependencies (see requirements.txt)

## Installation

1. Ensure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

2. Set your Cerebras API key in the `config.json` file:

```json
{
    "cerebras_api_key": "YOUR_CEREBRAS_API_KEY_HERE"
    ...
}
```

## Usage

### Basic Usage

```bash
python sql_scanner.py --path sample_code/inefficient_queries.sql
```

### Additional Options

```bash
python sql_scanner.py --path /path/to/your/sql/file.sql --output custom_report.md
```

### Command Line Arguments

- `--path`: Path to the SQL file or directory containing SQL files to scan (default: sample_code/inefficient_queries.sql)
- `--output`: Output file for the scan report (default: sql_scan_report.md)
- `--config`: Path to configuration file (default: config.json)
- `--categories`: Specific SQL performance categories to scan for (default: "SQL-specific Performance Tuning")

## SQL Performance Issues Detected

The scanner can identify various SQL performance issues, including:

1. **SELECT * Usage** - Using SELECT * instead of specifying needed columns
2. **Missing Indexes** - Queries that would benefit from proper indexing
3. **Missing WHERE Clauses** - Queries that scan entire tables unnecessarily
4. **Suboptimal Join Order** - Inefficient join sequences
5. **Non-SARGable Conditions** - Conditions that prevent index usage
6. **Missing LIMIT Clauses** - Queries that return unnecessarily large result sets
7. **Unnecessary DISTINCT** - Inefficient use of DISTINCT
8. **UNION vs UNION ALL** - Using UNION when UNION ALL would be more efficient

## Example Report

The scanner generates a comprehensive Markdown report that includes:

- Summary of issues found
- Detailed analysis of each issue
- Recommendations for optimization
- Code examples showing improved queries

## Extending the Scanner

You can add new SQL performance categories by adding new prompt templates to the `proprompts.json` file. Each template should include:

- `language`: "SQL"
- `category`: The performance category
- `subcategory`: The specific issue type
- `prompt_template`: The instruction for the model
- `output_format`: Expected output format
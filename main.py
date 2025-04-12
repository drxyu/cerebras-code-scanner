#!/usr/bin/env python3
"""
Cerebras Code Scanner - Hackathon Project

A tool that leverages Cerebras-hosted Llama 4 model to scan Python code for security
vulnerabilities and performance issues.
"""

import os
import sys
import json
import argparse
from pathlib import Path

from scanner.code_analyzer import CodeAnalyzer
from scanner.report_generator import ReportGenerator
from scanner.utils import setup_logging, load_config

# Setup logging
logger = setup_logging()

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Scan Python code for security vulnerabilities and performance issues using Cerebras and Llama 4."
    )
    parser.add_argument(
        "--path", 
        type=str, 
        default=".",
        help="Path to the Python codebase to scan (file or directory)"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="scan_report.md",
        help="Output file for the scan report"
    )
    parser.add_argument(
        "--config", 
        type=str, 
        default="config.json",
        help="Path to configuration file"
    )
    parser.add_argument(
        "--categories", 
        type=str, 
        nargs="+",
        help="Specific vulnerability categories to scan for"
    )
    return parser.parse_args()

def main():
    """Main entry point for the application."""
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Initialize the code analyzer
    analyzer = CodeAnalyzer(config)
    
    # Scan the codebase
    target_path = Path(args.path).resolve()
    if not target_path.exists():
        logger.error(f"Path does not exist: {target_path}")
        sys.exit(1)
        
    logger.info(f"Scanning codebase at: {target_path}")
    results = analyzer.scan_codebase(target_path, categories=args.categories)
    
    # Generate report
    report_generator = ReportGenerator()
    report_path = Path(args.output).resolve()
    report_generator.generate_report(results, report_path)
    
    logger.info(f"Scan complete. Report saved to: {report_path}")
    
    # Print summary
    print(f"\nScan Summary:")
    print(f"  Files scanned: {results['stats']['files_scanned']}")
    print(f"  Issues found: {results['stats']['total_issues']}")
    print(f"  Report saved to: {report_path}")

if __name__ == "__main__":
    main()
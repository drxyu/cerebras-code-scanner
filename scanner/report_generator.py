\"""Report Generator module for the Cerebras Code Scanner.

This module contains the ReportGenerator class that is responsible for generating
formatted reports of the scan results.
"""

import json
from pathlib import Path
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generates formatted reports of scan results.
    
    This class is responsible for taking the issues found by the code analyzer
    and generating a readable report in Markdown format.
    """
    
    def __init__(self):
        """Initialize the ReportGenerator."""
        pass
    
    def generate_report(self, results: Dict[str, Any], output_path: Path) -> None:
        """Generate a report of the scan results.
        
        Args:
            results: The scan results dictionary.
            output_path: Path to save the report to.
        """
        try:
            # Generate markdown report
            if output_path.suffix.lower() == ".md":
                self._generate_markdown_report(results, output_path)
            # Generate JSON report
            elif output_path.suffix.lower() == ".json":
                self._generate_json_report(results, output_path)
            else:
                # Default to markdown
                self._generate_markdown_report(results, output_path)
                
            logger.info(f"Report generated successfully: {output_path}")
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
    
    def _generate_markdown_report(self, results: Dict[str, Any], output_path: Path) -> None:
        """Generate a markdown report of the scan results.
        
        Args:
            results: The scan results dictionary.
            output_path: Path to save the report to.
        """
        issues = results["issues"]
        stats = results["stats"]
        
        # Create report content
        report = []
        
        # Add header
        report.append("# Cerebras Code Scanner Report")
        report.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        report.append("")
        
        # Add summary
        report.append("## Summary")
        report.append(f"- **Files Scanned**: {stats['files_scanned']}")
        report.append(f"- **Total Issues Found**: {stats['total_issues']}")
        report.append("")
        
        # Add issues by category
        report.append("### Issues by Category")
        for category, count in stats.get("categories", {}).items():
            report.append(f"- **{category}**: {count} issues")
        report.append("")
        
        # Group issues by file
        issues_by_file = {}
        for issue in issues:
            file_path = issue["file_path"]
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        # Add detailed findings
        report.append("## Detailed Findings")
        
        if not issues:
            report.append("*No issues found.*")
        else:
            # Sort files by number of issues (descending)
            sorted_files = sorted(issues_by_file.keys(), 
                                 key=lambda x: len(issues_by_file[x]), 
                                 reverse=True)
            
            for file_path in sorted_files:
                file_issues = issues_by_file[file_path]
                report.append(f"### {file_path}")
                report.append(f"*{len(file_issues)} issues found*")
                report.append("")
                
                # Group by category and subcategory
                by_category = {}
                for issue in file_issues:
                    category = issue["category"]
                    subcategory = issue["subcategory"]
                    key = f"{category} - {subcategory}"
                    
                    if key not in by_category:
                        by_category[key] = []
                    by_category[key].append(issue)
                
                # Add issues grouped by category
                for cat_key, cat_issues in by_category.items():
                    report.append(f"#### {cat_key}")
                    
                    for i, issue in enumerate(cat_issues, 1):
                        report.append(f"**Issue {i}**:")
                        report.append(issue["description"])
                        report.append("")
                    
                    report.append("")
        
        # Write report to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
    
    def _generate_json_report(self, results: Dict[str, Any], output_path: Path) -> None:
        """Generate a JSON report of the scan results.
        
        Args:
            results: The scan results dictionary.
            output_path: Path to save the report to.
        """
        # Add timestamp to results
        results["timestamp"] = datetime.now().isoformat()
        
        # Write JSON report to file
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
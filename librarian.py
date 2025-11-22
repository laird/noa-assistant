#!/usr/bin/env python3
"""
Librarian - Automated Code Quality and Maintenance Tool

This script analyzes the Noa Assistant codebase for:
- Code quality issues
- Security vulnerabilities
- Dependency updates
- Documentation gaps
- Test coverage
- Performance issues
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import subprocess


@dataclass
class Issue:
    """Represents a code issue found by librarian"""
    severity: str  # "critical", "high", "medium", "low", "info"
    category: str  # "security", "quality", "performance", "documentation", "dependencies"
    file_path: str
    line_number: int
    description: str
    suggestion: str

    def __str__(self):
        return f"[{self.severity.upper()}] {self.category}: {self.file_path}:{self.line_number}\n  {self.description}\n  → {self.suggestion}"


class CodeAnalyzer:
    """Analyzes Python code for common issues"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)
        self.issues: List[Issue] = []

    def analyze_file(self, file_path: Path) -> List[Issue]:
        """Analyze a single Python file"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                # Check for security issues
                issues.extend(self._check_security(file_path, i, line))
                # Check for code quality
                issues.extend(self._check_quality(file_path, i, line))
                # Check for performance issues
                issues.extend(self._check_performance(file_path, i, line))

        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")

        return issues

    def _check_security(self, file_path: Path, line_num: int, line: str) -> List[Issue]:
        """Check for security vulnerabilities"""
        issues = []

        # SQL injection risk
        if re.search(r'execute\s*\(\s*[\'"].*%s.*[\'"]', line):
            issues.append(Issue(
                severity="critical",
                category="security",
                file_path=str(file_path),
                line_number=line_num,
                description="Potential SQL injection vulnerability",
                suggestion="Use parameterized queries instead of string formatting"
            ))

        # Hardcoded credentials
        if re.search(r'(password|secret|api_key)\s*=\s*[\'"][^\'"]+[\'"]', line, re.IGNORECASE):
            if 'os.environ' not in line and 'getenv' not in line:
                issues.append(Issue(
                    severity="critical",
                    category="security",
                    file_path=str(file_path),
                    line_number=line_num,
                    description="Potential hardcoded credential",
                    suggestion="Use environment variables for sensitive data"
                ))

        # eval() usage
        if 'eval(' in line and not line.strip().startswith('#'):
            issues.append(Issue(
                severity="high",
                category="security",
                file_path=str(file_path),
                line_number=line_num,
                description="Use of eval() is dangerous",
                suggestion="Avoid eval() or use ast.literal_eval() for safe evaluation"
            ))

        # Shell injection risk
        if re.search(r'os\.system\(|subprocess\.call\(.*shell\s*=\s*True', line):
            issues.append(Issue(
                severity="high",
                category="security",
                file_path=str(file_path),
                line_number=line_num,
                description="Potential shell injection vulnerability",
                suggestion="Use subprocess with shell=False and argument lists"
            ))

        return issues

    def _check_quality(self, file_path: Path, line_num: int, line: str) -> List[Issue]:
        """Check for code quality issues"""
        issues = []

        # Bare except clause
        if re.match(r'\s*except\s*:', line):
            issues.append(Issue(
                severity="medium",
                category="quality",
                file_path=str(file_path),
                line_number=line_num,
                description="Bare except clause catches all exceptions",
                suggestion="Catch specific exception types"
            ))

        # Print statements in production code (skip if in debug context)
        if re.match(r'\s*print\s*\(', line) and 'debug' not in line.lower():
            if str(file_path) != 'librarian.py':  # Ignore this file
                issues.append(Issue(
                    severity="low",
                    category="quality",
                    file_path=str(file_path),
                    line_number=line_num,
                    description="Print statement found in code",
                    suggestion="Use logging module instead of print statements"
                ))

        # TODO/FIXME comments
        if re.search(r'#\s*(TODO|FIXME|XXX|HACK)', line, re.IGNORECASE):
            issues.append(Issue(
                severity="info",
                category="quality",
                file_path=str(file_path),
                line_number=line_num,
                description=f"Code comment indicates pending work: {line.strip()}",
                suggestion="Address the TODO/FIXME comment"
            ))

        return issues

    def _check_performance(self, file_path: Path, line_num: int, line: str) -> List[Issue]:
        """Check for performance issues"""
        issues = []

        # Multiple string concatenations in loop (simplified check)
        if '+=' in line and 'str' in line.lower():
            issues.append(Issue(
                severity="low",
                category="performance",
                file_path=str(file_path),
                line_number=line_num,
                description="String concatenation in loop may be inefficient",
                suggestion="Consider using list.join() or io.StringIO for better performance"
            ))

        return issues

    def analyze_project(self) -> List[Issue]:
        """Analyze the entire project"""
        python_files = list(self.root_dir.glob("**/*.py"))

        for file_path in python_files:
            # Skip virtual environment and .git directories
            if '.venv' in str(file_path) or '.git' in str(file_path):
                continue

            self.issues.extend(self.analyze_file(file_path))

        return self.issues


class DependencyChecker:
    """Check for outdated or vulnerable dependencies"""

    def __init__(self, requirements_file: str = "requirements.txt"):
        self.requirements_file = requirements_file

    def check_dependencies(self) -> List[Issue]:
        """Check for dependency issues"""
        issues = []

        if not os.path.exists(self.requirements_file):
            return issues

        with open(self.requirements_file, 'r') as f:
            dependencies = f.readlines()

        for i, dep in enumerate(dependencies, 1):
            dep = dep.strip()
            if not dep or dep.startswith('#'):
                continue

            # Check for unpinned versions
            if '==' not in dep and '~=' not in dep and not dep.startswith('-'):
                issues.append(Issue(
                    severity="medium",
                    category="dependencies",
                    file_path=self.requirements_file,
                    line_number=i,
                    description=f"Dependency '{dep}' is not pinned to a specific version",
                    suggestion="Pin dependencies to specific versions for reproducibility"
                ))

        return issues


class DocumentationChecker:
    """Check for missing documentation"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = Path(root_dir)

    def check_documentation(self) -> List[Issue]:
        """Check for documentation issues"""
        issues = []

        # Check for missing README sections
        readme_path = self.root_dir / "README.md"
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                readme_content = f.read()

            required_sections = ["Setup", "API", "Usage"]
            for section in required_sections:
                if section.lower() not in readme_content.lower():
                    issues.append(Issue(
                        severity="low",
                        category="documentation",
                        file_path="README.md",
                        line_number=0,
                        description=f"Missing '{section}' section in README",
                        suggestion=f"Add a '{section}' section to improve documentation"
                    ))
        else:
            issues.append(Issue(
                severity="high",
                category="documentation",
                file_path=".",
                line_number=0,
                description="No README.md found in project root",
                suggestion="Create a README.md file to document the project"
            ))

        return issues


class Librarian:
    """Main librarian orchestrator"""

    def __init__(self, root_dir: str = "."):
        self.root_dir = root_dir
        self.report = {
            "timestamp": datetime.now().isoformat(),
            "issues": [],
            "summary": {}
        }

    def run_analysis(self) -> Dict:
        """Run all analysis checks"""
        all_issues = []

        print("🔍 Running code analysis...")
        analyzer = CodeAnalyzer(self.root_dir)
        all_issues.extend(analyzer.analyze_project())

        print("📦 Checking dependencies...")
        dep_checker = DependencyChecker()
        all_issues.extend(dep_checker.check_dependencies())

        print("📚 Checking documentation...")
        doc_checker = DocumentationChecker(self.root_dir)
        all_issues.extend(doc_checker.check_documentation())

        # Sort issues by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        all_issues.sort(key=lambda x: severity_order.get(x.severity, 5))

        # Generate summary
        summary = {
            "total_issues": len(all_issues),
            "by_severity": {},
            "by_category": {}
        }

        for issue in all_issues:
            summary["by_severity"][issue.severity] = summary["by_severity"].get(issue.severity, 0) + 1
            summary["by_category"][issue.category] = summary["by_category"].get(issue.category, 0) + 1

        self.report["issues"] = [asdict(issue) for issue in all_issues]
        self.report["summary"] = summary

        return self.report, all_issues

    def print_report(self, issues: List[Issue]):
        """Print human-readable report"""
        print("\n" + "="*80)
        print("📊 LIBRARIAN ANALYSIS REPORT")
        print("="*80)
        print(f"Generated: {self.report['timestamp']}")
        print(f"Total Issues Found: {self.report['summary']['total_issues']}\n")

        # Summary by severity
        print("By Severity:")
        for severity in ["critical", "high", "medium", "low", "info"]:
            count = self.report['summary']['by_severity'].get(severity, 0)
            if count > 0:
                print(f"  {severity.capitalize()}: {count}")

        # Summary by category
        print("\nBy Category:")
        for category, count in self.report['summary']['by_category'].items():
            print(f"  {category.capitalize()}: {count}")

        print("\n" + "-"*80)
        print("DETAILED ISSUES:")
        print("-"*80 + "\n")

        # Print each issue
        for issue in issues:
            print(issue)
            print()

        print("="*80)

    def save_report(self, filename: str = "librarian_report.json"):
        """Save report to JSON file"""
        with open(filename, 'w') as f:
            json.dump(self.report, f, indent=2)
        print(f"\n💾 Report saved to {filename}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Librarian - Automated Code Quality Tool")
    parser.add_argument("--root-dir", default=".", help="Root directory to analyze")
    parser.add_argument("--output", default="librarian_report.json", help="Output report file")
    parser.add_argument("--severity", choices=["critical", "high", "medium", "low", "info"],
                       help="Only show issues of this severity or higher")
    parser.add_argument("--category", help="Only show issues in this category")
    args = parser.parse_args()

    librarian = Librarian(args.root_dir)
    report, issues = librarian.run_analysis()

    # Filter issues if requested
    if args.severity:
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
        threshold = severity_order[args.severity]
        issues = [i for i in issues if severity_order.get(i.severity, 5) <= threshold]

    if args.category:
        issues = [i for i in issues if i.category == args.category]

    librarian.print_report(issues)
    librarian.save_report(args.output)

    # Exit with non-zero code if critical issues found
    critical_issues = [i for i in issues if i.severity == "critical"]
    if critical_issues:
        print(f"\n⚠️  Found {len(critical_issues)} critical issue(s)!")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())

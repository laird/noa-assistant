# Librarian - Automated Code Quality Tool

Librarian is an automated code quality analysis and improvement tool for the Noa Assistant project. It helps maintain code quality by identifying issues, security vulnerabilities, and improvement opportunities.

## Features

- 🔒 **Security Analysis**: Detects potential security vulnerabilities
  - SQL injection risks
  - Hardcoded credentials
  - Shell injection vulnerabilities
  - Dangerous eval() usage

- 🎯 **Code Quality Checks**: Identifies code quality issues
  - Bare except clauses
  - Print statements in production code
  - TODO/FIXME comments
  - Code complexity issues

- ⚡ **Performance Analysis**: Finds performance bottlenecks
  - Inefficient string concatenation
  - Loop optimization opportunities

- 📚 **Documentation Checks**: Ensures proper documentation
  - README completeness
  - Missing docstrings
  - API documentation

- 📦 **Dependency Management**: Manages project dependencies
  - Unpinned dependency versions
  - Outdated packages
  - Security vulnerabilities in dependencies

## Installation

No additional installation required! Librarian uses only Python standard library.

```bash
# Make the scripts executable
chmod +x librarian.sh librarian.py
```

## Usage

### Quick Start

Run a basic analysis:

```bash
./librarian.sh
```

Or use the Python script directly:

```bash
python3 librarian.py
```

### Command Line Options

**Bash Script (`librarian.sh`)**:

```bash
# Run analysis only (default)
./librarian.sh --analyze

# Run analysis and attempt auto-fixes
./librarian.sh --fix

# Filter by severity
./librarian.sh --severity critical

# Filter by category
./librarian.sh --category security

# Show only report from previous run
./librarian.sh --report

# Show help
./librarian.sh --help
```

**Python Script (`librarian.py`)**:

```bash
# Basic analysis
python3 librarian.py

# Specify output file
python3 librarian.py --output custom_report.json

# Filter by severity
python3 librarian.py --severity high

# Filter by category
python3 librarian.py --category security

# Analyze specific directory
python3 librarian.py --root-dir /path/to/project
```

### Configuration

Configure librarian behavior using `.librarian.yml`:

```yaml
# Minimum severity level to report
min_severity: medium

# Categories to analyze
categories:
  - security
  - quality
  - performance
  - documentation
  - dependencies

# Directories to exclude
exclude:
  - .venv/
  - __pycache__/
  - .git/
```

## Understanding the Report

### Severity Levels

- **Critical**: Security vulnerabilities or major issues requiring immediate attention
- **High**: Important issues that should be addressed soon
- **Medium**: Issues that should be planned for resolution
- **Low**: Minor issues or style improvements
- **Info**: Informational findings (TODO comments, etc.)

### Categories

- **Security**: Security vulnerabilities and risks
- **Quality**: Code quality and maintainability issues
- **Performance**: Performance optimization opportunities
- **Documentation**: Documentation gaps and improvements
- **Dependencies**: Dependency management issues

### Example Report

```
📊 LIBRARIAN ANALYSIS REPORT
Generated: 2025-11-22T15:30:00
Total Issues Found: 15

By Severity:
  Critical: 2
  High: 3
  Medium: 5
  Low: 5

By Category:
  Security: 3
  Quality: 7
  Performance: 2
  Documentation: 3
```

## Continuous Integration

### GitHub Actions

Add librarian to your CI pipeline:

```yaml
name: Code Quality

on: [push, pull_request]

jobs:
  librarian:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Run Librarian
        run: |
          python3 librarian.py --severity high
      - name: Upload Report
        uses: actions/upload-artifact@v2
        with:
          name: librarian-report
          path: librarian_report.json
```

## Best Practices

### Running Regularly

1. **Before commits**: Run librarian before creating commits
2. **In CI/CD**: Integrate into your CI/CD pipeline
3. **Weekly reviews**: Schedule weekly reviews of librarian reports
4. **Pre-release**: Always run before releases

### Addressing Issues

1. **Start with Critical**: Address critical security issues immediately
2. **Plan High Priority**: Create tasks for high-priority issues
3. **Batch Medium/Low**: Group similar medium/low issues for efficiency
4. **Track Progress**: Use the JSON report to track improvements over time

### Custom Checks

Extend librarian by modifying `librarian.py`:

```python
def _check_custom(self, file_path: Path, line_num: int, line: str) -> List[Issue]:
    """Add your custom checks here"""
    issues = []

    # Your custom logic
    if "your_pattern" in line:
        issues.append(Issue(
            severity="medium",
            category="quality",
            file_path=str(file_path),
            line_number=line_num,
            description="Your description",
            suggestion="Your suggestion"
        ))

    return issues
```

## Automation

### Automated Improvement Loop

For continuous improvement, you can create automated improvement sessions:

1. Run librarian to identify issues
2. Prioritize issues by severity
3. Create focused improvement tasks
4. Track progress over time

### Example Workflow

```bash
# 1. Analyze codebase
./librarian.sh --analyze

# 2. Review critical issues
./librarian.sh --severity critical

# 3. Fix security issues first
./librarian.sh --category security

# 4. Track progress
git add .
git commit -m "fix: address librarian security issues"
```

## Troubleshooting

### Common Issues

**"No module named 'xyz'"**
- Ensure all dependencies are installed: `pip install -r requirements.txt`

**"Permission denied"**
- Make scripts executable: `chmod +x librarian.sh librarian.py`

**"Command not found: jq"**
- Install jq for JSON parsing: `apt-get install jq` or `brew install jq`
- Or use Python script directly (doesn't require jq)

## Contributing

To add new checks to librarian:

1. Add your check method to the appropriate class in `librarian.py`
2. Update the configuration schema in `.librarian.yml`
3. Add documentation for the new check
4. Test thoroughly

## License

Same license as the Noa Assistant project.

## Support

For issues or questions:
1. Check this documentation
2. Review the librarian source code
3. Create an issue in the project repository

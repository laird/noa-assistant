#!/bin/bash

# Librarian - Automated Code Quality and Improvement Script
# This script runs the librarian tool and optionally creates fixes

set -e

LOG_FILE="librarian.log"
REPORT_FILE="librarian_report.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_message() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ✓ $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ⚠ $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ✗ $1" | tee -a "$LOG_FILE"
}

# Usage information
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Librarian - Automated code quality analysis and improvement tool

OPTIONS:
    -a, --analyze       Run code analysis only (default)
    -f, --fix           Run analysis and attempt to fix issues
    -s, --severity      Minimum severity level (critical, high, medium, low, info)
    -c, --category      Filter by category (security, quality, performance, documentation, dependencies)
    -r, --report        Generate report only from previous run
    -h, --help          Show this help message

EXAMPLES:
    $0                          # Run analysis with default settings
    $0 --analyze                # Run analysis only
    $0 --fix                    # Run analysis and auto-fix issues
    $0 --severity critical      # Show only critical issues
    $0 --category security      # Show only security issues

EOF
    exit 0
}

# Check if Python is installed
check_python() {
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is not installed"
        exit 1
    fi
}

# Run the librarian analysis
run_analysis() {
    local severity=$1
    local category=$2

    log_message "Starting librarian analysis..."

    local args=""
    if [ -n "$severity" ]; then
        args="$args --severity $severity"
    fi
    if [ -n "$category" ]; then
        args="$args --category $category"
    fi

    if python3 librarian.py $args; then
        log_success "Analysis completed successfully"
        return 0
    else
        exit_code=$?
        if [ $exit_code -eq 1 ]; then
            log_warning "Analysis completed with critical issues found"
        else
            log_error "Analysis failed with exit code $exit_code"
        fi
        return $exit_code
    fi
}

# Auto-fix common issues
auto_fix_issues() {
    log_message "Auto-fixing common issues..."

    # Example: Convert print statements to logging (simplified)
    # This is a placeholder - actual implementation would be more sophisticated

    if [ -f "$REPORT_FILE" ]; then
        local print_issues=$(jq -r '.issues[] | select(.category=="quality" and .description | contains("Print statement")) | .file_path' "$REPORT_FILE" 2>/dev/null | sort -u)

        if [ -n "$print_issues" ]; then
            log_message "Found files with print statements that could be converted to logging"
            echo "$print_issues"
        fi
    fi

    log_message "Auto-fix complete. Manual review may be required."
}

# Generate improvement suggestions
generate_suggestions() {
    if [ ! -f "$REPORT_FILE" ]; then
        log_error "No report file found. Run analysis first."
        return 1
    fi

    log_message "Generating improvement suggestions..."

    local critical_count=$(jq -r '.summary.by_severity.critical // 0' "$REPORT_FILE")
    local high_count=$(jq -r '.summary.by_severity.high // 0' "$REPORT_FILE")
    local medium_count=$(jq -r '.summary.by_severity.medium // 0' "$REPORT_FILE")

    echo ""
    echo "======================================================================"
    echo "IMPROVEMENT PRIORITIES"
    echo "======================================================================"
    echo ""

    if [ "$critical_count" -gt 0 ]; then
        echo "🔴 CRITICAL: $critical_count issue(s) - Address immediately"
        jq -r '.issues[] | select(.severity=="critical") | "  • \(.file_path):\(.line_number) - \(.description)"' "$REPORT_FILE"
        echo ""
    fi

    if [ "$high_count" -gt 0 ]; then
        echo "🟠 HIGH: $high_count issue(s) - Address soon"
        jq -r '.issues[] | select(.severity=="high") | "  • \(.file_path):\(.line_number) - \(.description)"' "$REPORT_FILE" | head -5
        if [ "$high_count" -gt 5 ]; then
            echo "  ... and $((high_count - 5)) more"
        fi
        echo ""
    fi

    if [ "$medium_count" -gt 0 ]; then
        echo "🟡 MEDIUM: $medium_count issue(s) - Plan to address"
        echo ""
    fi

    echo "Run 'cat $REPORT_FILE | jq' for full details"
    echo "======================================================================"
}

# Main script logic
main() {
    check_python

    local mode="analyze"
    local severity=""
    local category=""

    # Parse command line arguments
    while [ "$#" -gt 0 ]; do
        case "$1" in
            -a|--analyze)
                mode="analyze"
                shift
                ;;
            -f|--fix)
                mode="fix"
                shift
                ;;
            -s|--severity)
                severity="$2"
                shift 2
                ;;
            -c|--category)
                category="$2"
                shift 2
                ;;
            -r|--report)
                mode="report"
                shift
                ;;
            -h|--help)
                usage
                ;;
            *)
                log_error "Unknown option: $1"
                usage
                ;;
        esac
    done

    echo ""
    echo "======================================================================"
    echo "🔍 LIBRARIAN - Code Quality Analysis Tool"
    echo "======================================================================"
    echo ""

    case "$mode" in
        analyze)
            run_analysis "$severity" "$category"
            generate_suggestions
            ;;
        fix)
            run_analysis "$severity" "$category"
            auto_fix_issues
            generate_suggestions
            ;;
        report)
            generate_suggestions
            ;;
    esac

    echo ""
    log_success "Librarian completed"
    echo ""
}

# Run main function
main "$@"

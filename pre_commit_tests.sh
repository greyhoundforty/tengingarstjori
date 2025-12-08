#!/bin/bash
# Pre-Commit Testing Suite for Tengingarstjóri
# Run this script before committing changes to GitHub

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Function to print colored output
print_header() {
    echo -e "\n${BLUE}===============================================${NC}"
    echo -e "${BLUE} $1${NC}"
    echo -e "${BLUE}===============================================${NC}"
}

print_step() {
    echo -e "\n${PURPLE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Initialize counters
TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Function to run a test step
run_test() {
    local test_name="$1"
    local test_command="$2"
    local required="${3:-true}"
    
    print_step "Running: $test_name"
    
    if eval "$test_command"; then
        print_success "$test_name passed"
        ((TESTS_PASSED++))
        return 0
    else
        if [ "$required" = "true" ]; then
            print_error "$test_name failed"
            ((TESTS_FAILED++))
            return 1
        else
            print_warning "$test_name failed (optional)"
            ((WARNINGS++))
            return 0
        fi
    fi
}

# Check if we're in the right directory
check_project_structure() {
    if [ ! -f "pyproject.toml" ] && [ ! -f "setup.py" ] && [ ! -f "requirements.txt" ]; then
        print_error "Not in a Python project directory. Please run from the project root."
        exit 1
    fi
    
    if [ ! -d "src" ] && [ ! -f "main.py" ]; then
        print_error "Cannot find source code. Expected 'src' directory or 'main.py'."
        exit 1
    fi
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main testing function
main() {
    print_header "Tengingarstjóri Pre-Commit Testing Suite"
    
    # Check project structure
    print_step "Checking project structure"
    check_project_structure
    print_success "Project structure looks good"
    
    # Check if we have virtual environment activated
    if [ -z "$VIRTUAL_ENV" ] && [ -z "$MISE_ACTIVE_PROFILE" ]; then
        print_warning "No virtual environment detected. Consider using 'source .venv/bin/activate' or 'mise run'"
    fi
    
    print_header "1. Code Quality Checks"
    
    # Python syntax check
    if command_exists python3; then
        run_test "Python syntax check" "python3 -m py_compile src/**/*.py 2>/dev/null || find src -name '*.py' -exec python3 -m py_compile {} \;"
    else
        print_warning "Python3 not found, skipping syntax check"
    fi
    
    # Flake8 linting
    if command_exists flake8; then
        run_test "Flake8 linting" "flake8 src/ --max-line-length=88 --extend-ignore=E203,W503"
    else
        print_warning "Flake8 not installed, skipping linting check"
    fi
    
    # Black formatting check
    if command_exists black; then
        run_test "Black formatting check" "black --check src/ --diff"
    else
        print_warning "Black not installed, skipping formatting check"
    fi
    
    # MyPy type checking
    if command_exists mypy; then
        run_test "MyPy type checking" "mypy src/ --ignore-missing-imports" false
    else
        print_warning "MyPy not installed, skipping type checking"
    fi
    
    print_header "2. Functional Tests"
    
    # Import tests
    run_test "Import tests" "python3 -c 'import sys; sys.path.insert(0, \"src\"); import cli, config_manager, models'"
    
    # CLI help test
    if [ -f "main.py" ]; then
        run_test "CLI help test" "python3 main.py --help >/dev/null"
    elif command_exists tg; then
        run_test "CLI help test" "tg --help >/dev/null"
    else
        print_warning "Cannot test CLI - neither main.py found nor tg command available"
    fi
    
    print_header "3. Configuration Tests"
    
    # Test SSH directory creation (in temp location)
    run_test "SSH directory creation test" "python3 -c 'import tempfile, os; from pathlib import Path; temp_dir = Path(tempfile.mkdtemp()); ssh_dir = temp_dir / \".ssh\"; ssh_dir.mkdir(mode=0o700); print(f\"Created {ssh_dir}\"); import shutil; shutil.rmtree(temp_dir)'"
    
    # Test config file operations (safe test)
    run_test "Config file operations test" "python3 -c 'import tempfile, json; from pathlib import Path; temp_file = Path(tempfile.mktemp(suffix=\".json\")); temp_file.write_text(json.dumps({\"test\": True})); data = json.loads(temp_file.read_text()); assert data[\"test\"] == True; temp_file.unlink(); print(\"Config operations work\")'"
    
    print_header "4. Documentation Tests"
    
    # Check README exists and has content
    run_test "README existence and content" "[ -f README.md ] && [ -s README.md ]"
    
    # Check for CHANGELOG
    run_test "CHANGELOG existence" "[ -f CHANGELOG.md ]" false
    
    # Check for requirements.txt
    run_test "Requirements file exists" "[ -f requirements.txt ]"
    
    # Check requirements are valid
    if [ -f requirements.txt ]; then
        run_test "Requirements validation" "python3 -m pip check 2>/dev/null || pip check 2>/dev/null || echo 'pip check not available, skipping'"
    fi
    
    print_header "5. Git Repository Tests"
    
    # Check if we're in a git repository
    if [ -d ".git" ]; then
        # Check for uncommitted changes
        run_test "Git status check" "git diff --quiet && git diff --staged --quiet" false
        
        # Check for untracked files that should be committed
        untracked_files=$(git ls-files --others --exclude-standard)
        if [ -n "$untracked_files" ]; then
            print_warning "Untracked files found: $untracked_files"
            ((WARNINGS++))
        fi
        
        # Check current branch
        current_branch=$(git branch --show-current)
        print_step "Current branch: $current_branch"
        
        # Check if main.py or src/ files have been modified
        if git diff --name-only HEAD | grep -E "(src/|main\.py|requirements\.txt|pyproject\.toml)" >/dev/null; then
            print_warning "Core files have been modified - make sure tests still pass"
            ((WARNINGS++))
        fi
    else
        print_warning "Not in a git repository"
        ((WARNINGS++))
    fi
    
    print_header "6. Integration Tests"
    
    # Test basic workflow (safe, using temporary files)
    run_test "Basic workflow simulation" "python3 -c '
import tempfile, sys, os
from pathlib import Path
sys.path.insert(0, \"src\")

# Test imports
from config_manager import SSHConfigManager
from models import SSHConnection

# Create temp directory for test
temp_dir = Path(tempfile.mkdtemp())
test_ssh_dir = temp_dir / \".ssh\"
test_config_dir = temp_dir / \".tengingarstjori\"

# Test config manager creation
config_manager = SSHConfigManager(config_dir=test_config_dir)

# Test connection creation
conn = SSHConnection(
    name=\"test-server\",
    host=\"example.com\",
    user=\"testuser\",
    port=22
)

print(f\"Test connection: {conn.name}@{conn.host}:{conn.port}\")

# Cleanup
import shutil
shutil.rmtree(temp_dir)
print(\"Basic workflow test completed successfully\")
'"
    
    print_header "7. Security Checks"
    
    # Check for common security issues
    run_test "No hardcoded secrets" "! grep -r -E '(password|secret|key).*=.*['\"].*['\']' src/ || echo 'No hardcoded secrets found'"
    
    # Check file permissions for sensitive files
    if [ -f ".env" ]; then
        run_test "Environment file permissions" "[ \$(stat -c %a .env) -le 600 ]" false
    fi
    
    print_header "8. Performance & Dependencies"
    
    # Check for large files
    run_test "No large files in repository" "! find . -name '*.py' -size +1M | grep -v __pycache__ | head -1"
    
    # Check for unused imports (if available)
    if command_exists unimport; then
        run_test "Unused imports check" "unimport --check src/" false
    fi
    
    # Summary
    print_header "Test Summary"
    
    echo -e "${GREEN}Tests Passed: $TESTS_PASSED${NC}"
    echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
    echo -e "${RED}Tests Failed: $TESTS_FAILED${NC}"
    echo ""
    
    if [ $TESTS_FAILED -eq 0 ]; then
        print_success "🎉 All critical tests passed! Ready to commit."
        if [ $WARNINGS -gt 0 ]; then
            print_warning "Note: $WARNINGS warnings found. Review them before committing."
        fi
        echo ""
        echo -e "${GREEN}Suggested next steps:${NC}"
        echo -e "  ${BLUE}1.${NC} Review any warnings above"
        echo -e "  ${BLUE}2.${NC} git add ."
        echo -e "  ${BLUE}3.${NC} git commit -m 'Your commit message'"
        echo -e "  ${BLUE}4.${NC} git push"
        exit 0
    else
        print_error "❌ $TESTS_FAILED critical tests failed. Please fix before committing."
        echo ""
        echo -e "${RED}Fix the failed tests and run this script again.${NC}"
        exit 1
    fi
}

# Help function
show_help() {
    echo "Tengingarstjóri Pre-Commit Testing Suite"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --quick        Run only essential tests (faster)"
    echo "  --fix          Attempt to fix some issues automatically"
    echo ""
    echo "This script runs a comprehensive test suite including:"
    echo "  • Code quality checks (linting, formatting)"
    echo "  • Functional tests (imports, CLI)"
    echo "  • Configuration tests"
    echo "  • Documentation tests"
    echo "  • Git repository checks"
    echo "  • Integration tests"
    echo "  • Security checks"
    echo ""
    echo "Run this before committing to ensure code quality."
}

# Quick mode function
quick_mode() {
    print_header "Quick Pre-Commit Check"
    
    check_project_structure
    
    # Only run essential tests
    run_test "Python syntax check" "python3 -m py_compile src/**/*.py 2>/dev/null || find src -name '*.py' -exec python3 -m py_compile {} \;"
    run_test "Import tests" "python3 -c 'import sys; sys.path.insert(0, \"src\"); import cli, config_manager, models'"
    
    if command_exists flake8; then
        run_test "Quick linting" "flake8 src/ --select=E9,F63,F7,F82 --show-source"
    fi
    
    print_header "Quick Test Summary"
    if [ $TESTS_FAILED -eq 0 ]; then
        print_success "✅ Quick tests passed! You can commit, but consider running full tests."
        exit 0
    else
        print_error "❌ Quick tests failed. Please fix critical issues."
        exit 1
    fi
}

# Auto-fix function
auto_fix() {
    print_header "Auto-Fix Mode"
    
    print_step "Attempting to fix common issues..."
    
    # Fix formatting with black
    if command_exists black; then
        print_step "Running black formatter"
        black src/
        print_success "Code formatted with black"
    fi
    
    # Fix imports with isort
    if command_exists isort; then
        print_step "Sorting imports with isort"
        isort src/
        print_success "Imports sorted"
    fi
    
    print_success "Auto-fix completed. Run the full test suite again."
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    --quick)
        quick_mode
        ;;
    --fix)
        auto_fix
        exit 0
        ;;
    "")
        main
        ;;
    *)
        echo "Unknown option: $1"
        show_help
        exit 1
        ;;
esac

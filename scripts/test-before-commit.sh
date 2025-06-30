#!/bin/bash
set -e

echo "🧪 Running Pre-Commit Tests for Tengingarstjóri"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"
    
    print_status "Running: $test_name"
    TESTS_RUN=$((TESTS_RUN + 1))
    
    if eval "$test_command" > /tmp/test_output 2>&1; then
        print_success "$test_name"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        print_error "$test_name"
        echo "Output:"
        cat /tmp/test_output
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Ensure we're in the right directory
if [[ ! -f "pyproject.toml" ]] || [[ ! -d "src" ]]; then
    print_error "Please run this script from the tengingarstjóri project root"
    exit 1
fi

echo ""
print_status "Setting up test environment..."

# Install in development mode
if ! mise run dev > /dev/null 2>&1; then
    print_error "Failed to install in development mode"
    exit 1
fi

print_success "Development environment ready"

echo ""
print_status "Running test suite..."

# 1. Unit Tests
run_test "Unit Tests (Models)" "mise run test:unit"

# 2. CLI Integration Tests  
run_test "CLI Integration Tests" "mise run test:cli"

# 3. Code Quality Checks
run_test "Code Formatting (Black)" "python -m black --check src/ tests/"
run_test "Code Linting (Flake8)" "python -m flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503"
run_test "Type Checking (MyPy)" "python -m mypy src/ --ignore-missing-imports"

# 4. CLI Functionality Tests
echo ""
print_status "Testing CLI functionality..."

run_test "CLI Help" "tg --help"
run_test "CLI Version" "tg --version"

# Test CLI with actual commands (if initialized)
if tg config --help > /dev/null 2>&1; then
    run_test "CLI Config Help" "tg config --help"
    run_test "CLI Add Help" "tg add --help"
    run_test "CLI List Help" "tg list --help"
fi

# 5. Import Tests
run_test "Import Tests" "python -c 'from src.models import SSHConnection; from src.config_manager import SSHConfigManager; from src.cli import cli; print(\"All imports successful\")'"

# 6. Configuration Tests
echo ""
print_status "Testing configuration files..."

run_test "PyProject.toml Syntax" "python -c 'import tomllib; tomllib.load(open(\"pyproject.toml\", \"rb\"))'"
run_test "Requirements.txt Syntax" "python -m pip check"

# Summary
echo ""
echo "=============================================="
echo "Test Summary:"
echo "  Total: $TESTS_RUN"
echo "  Passed: $TESTS_PASSED"
echo "  Failed: $TESTS_FAILED"

if [[ $TESTS_FAILED -eq 0 ]]; then
    print_success "All tests passed! ✨"
    echo ""
    echo "🚀 Ready for commit/push to GitHub!"
    echo ""
    echo "Next steps:"
    echo "  git add ."
    echo "  git commit -m 'feat: add CLI arguments and fix newline issues'"
    echo "  git push origin main"
    exit 0
else
    print_error "Some tests failed!"
    echo ""
    echo "❌ Fix failing tests before committing"
    echo ""
    echo "Debug commands:"
    echo "  mise run test        # Run all tests"
    echo "  mise run lint        # Check code quality"
    echo "  mise run format      # Auto-format code"
    exit 1
fi

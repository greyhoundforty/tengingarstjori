#!/bin/bash
"""
Comprehensive Test PyPI Installation Test Script

This script tests the tengingarstjori package installation from Test PyPI
using multiple methods and Python versions.
"""

set -e  # Exit on any error

echo "🧪 Tengingarstjóri Test PyPI Installation Testing"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test results tracking
PASSED=0
FAILED=0

run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "${BLUE}Testing: ${test_name}${NC}"
    echo "Command: $test_command"
    echo "----------------------------------------"

    if eval "$test_command"; then
        echo -e "${GREEN}✅ PASSED: ${test_name}${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED: ${test_name}${NC}"
        ((FAILED++))
    fi
    echo ""
}

echo "🐳 Docker Tests"
echo "==============="

# Test 1: Basic Docker Installation Test
run_test "Docker Python 3.11 Installation" "
docker run --rm python:3.11-slim bash -c '
pip install --index-url https://test.pypi.org/simple/ tengingarstjori &&
python -c \"import tengingarstjori; print(f\"Success! Version: {tengingarstjori.__version__}\")\" &&
tg --version
'
"

# Test 2: Multi-Python Docker Tests
for python_version in "3.9" "3.10" "3.12"; do
    run_test "Docker Python ${python_version}" "
    docker run --rm python:${python_version}-slim bash -c '
    pip install --index-url https://test.pypi.org/simple/ tengingarstjori &&
    tg --version
    '
    "
done

echo "🌐 Local Virtual Environment Tests"
echo "=================================="

# Test 3: Python venv + pip
run_test "Local venv + pip" "
python -m venv test-env-pip &&
source test-env-pip/bin/activate &&
pip install --index-url https://test.pypi.org/simple/ tengingarstjori &&
python -c 'import tengingarstjori; print(f\"Version: {tengingarstjori.__version__}\")' &&
tg --version &&
deactivate &&
rm -rf test-env-pip
"

# Test 4: UV virtual environment
if command -v uv &> /dev/null; then
    run_test "Local uv + pip" "
    uv venv test-env-uv &&
    source test-env-uv/bin/activate &&
    uv pip install --index-url https://test.pypi.org/simple/ tengingarstjori &&
    python -c 'import tengingarstjori; print(f\"Version: {tengingarstjori.__version__}\")' &&
    tg --version &&
    deactivate &&
    rm -rf test-env-uv
    "
else
    echo -e "${YELLOW}⚠️  SKIPPED: uv not installed${NC}"
    echo ""
fi

# Test 5: Detailed functionality test
run_test "Detailed Functionality Test" "
python -m venv test-env-detailed &&
source test-env-detailed/bin/activate &&
pip install --index-url https://test.pypi.org/simple/ tengingarstjori &&
echo 'Testing imports...' &&
python -c '
import tengingarstjori
from tengingarstjori import SSHConnection, SSHConfigManager, cli
print(f\"✅ Package version: {tengingarstjori.__version__}\")
print(f\"✅ Author: {tengingarstjori.__author__}\")
print(f\"✅ Description: {tengingarstjori.__description__}\")

# Test model creation
conn = SSHConnection(name=\"test\", host=\"example.com\", user=\"user\")
print(f\"✅ Created SSH connection: {conn.name}\")

# Test config generation
config = conn.to_ssh_config_block()
print(f\"✅ Generated SSH config: {len(config)} characters\")

print(\"✅ All imports and basic functionality working!\")
' &&
echo 'Testing CLI...' &&
tg --version &&
tg --help > /dev/null &&
echo '✅ CLI commands working!' &&
deactivate &&
rm -rf test-env-detailed
"

echo "📊 Test Results Summary"
echo "======================"
echo -e "✅ Passed: ${GREEN}${PASSED}${NC}"
echo -e "❌ Failed: ${RED}${FAILED}${NC}"
echo -e "📊 Total:  $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All tests passed! Your Test PyPI package is working perfectly!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Test the package functionality in a real environment"
    echo "2. If everything looks good, publish to production PyPI"
    echo "3. Update your README with installation instructions"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Please check the output above.${NC}"
    echo ""
    echo "Common issues:"
    echo "1. Package not yet uploaded to Test PyPI"
    echo "2. Missing dependencies on Test PyPI"
    echo "3. Network connectivity issues"
    exit 1
fi

"""Test configuration for pytest."""

import sys
from pathlib import Path

# Add src directory to Python path for imports
# This allows importing from tengingarstjori package located in src/tengingarstjori/
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

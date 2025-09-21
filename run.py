#!/usr/bin/env python3
"""Simple runner script for rubber-duckers."""

import sys
from pathlib import Path

# Add src to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import and run
from main import run_bot
import asyncio

if __name__ == "__main__":
    exit_code = asyncio.run(run_bot())
    sys.exit(exit_code)

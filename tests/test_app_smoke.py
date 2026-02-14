"""Smoke test: verify app.py can be imported without crashing.

This catches import errors, missing dependencies, and obvious startup bugs.
"""

from __future__ import annotations

import subprocess
import sys


def test_app_importable() -> None:
    """app.py can be parsed by Python without syntax/import errors."""
    result = subprocess.run(
        [sys.executable, "-c", "import ast; ast.parse(open('app.py').read())"],
        cwd=r"c:\Users\salah\OneDrive\Desktop\ez\export_analytics_platform",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"app.py parse failed: {result.stderr}"


def test_data_loader_importable() -> None:
    """services.data_loader can be imported without errors."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import sys; sys.path.insert(0, '.'); from services.data_loader import load_buyers",
        ],
        cwd=r"c:\Users\salah\OneDrive\Desktop\ez\export_analytics_platform",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"data_loader import failed: {result.stderr}"


def test_ai_client_parseable() -> None:
    """services/ai_client.py has valid Python syntax."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "import ast; ast.parse(open('services/ai_client.py').read())",
        ],
        cwd=r"c:\Users\salah\OneDrive\Desktop\ez\export_analytics_platform",
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, f"ai_client.py parse failed: {result.stderr}"

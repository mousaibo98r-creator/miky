"""Shared test fixtures for the Export Analytics Platform test suite."""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Generator
from typing import Any

import pytest

SAMPLE_BUYERS: list[dict[str, Any]] = [
    {
        "buyer_name": "Test Corp Alpha",
        "destination_country": "USA",
        "total_invoices": 10,
        "total_usd": 50000.0,
        "exporters": {"Exporter A": 5, "Exporter B": 5},
        "company_name_english": "Test Corp Alpha",
        "country_english": "United States",
        "country_code": "+1",
        "email": ["alpha@test.com"],
        "website": ["https://test-alpha.com"],
        "phone": ["+1-555-0100"],
        "address": ["123 Test St, New York, NY 10001"],
    },
    {
        "buyer_name": "Beta Industries",
        "destination_country": "GERMANY",
        "total_invoices": 5,
        "total_usd": 25000.0,
        "exporters": {"Exporter C": 5},
        "company_name_english": "Beta Industries",
        "country_english": "Germany",
        "country_code": "+49",
        "email": ["info@beta.de"],
        "website": [],
        "phone": [],
        "address": [],
    },
    {
        "buyer_name": "Gamma Trading",
        "destination_country": "JAPAN",
        "total_invoices": 3,
        "total_usd": 75000.0,
        "exporters": {"Exporter D": 3},
        "company_name_english": "Gamma Trading",
        "country_english": "Japan",
        "country_code": "+81",
        "email": [],
        "website": ["https://gamma.jp"],
        "phone": ["+81-3-1234-5678"],
        "address": ["Tokyo, Japan"],
    },
]


@pytest.fixture
def sample_buyers() -> list[dict[str, Any]]:
    """Provide sample buyer data for tests."""
    return SAMPLE_BUYERS.copy()


@pytest.fixture
def temp_data_file(sample_buyers: list[dict[str, Any]]) -> Generator[str, None, None]:
    """Create a temporary JSON file with sample buyer data.

    Yields the file path. Cleaned up after the test.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        json.dump(sample_buyers, f, ensure_ascii=False)
        path = f.name

    yield path

    os.unlink(path)


@pytest.fixture
def empty_data_file() -> Generator[str, None, None]:
    """Create an empty temporary file. Yields the path."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
        path = f.name

    yield path

    os.unlink(path)

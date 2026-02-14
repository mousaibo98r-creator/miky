"""Tests for services.ai_client module."""

from __future__ import annotations

from services.ai_client import _clean_json


class TestCleanJson:
    """Tests for the _clean_json helper."""

    def test_plain_json(self) -> None:
        result = _clean_json('{"email": ["a@b.com"], "phone": []}')
        assert result is not None
        assert result["email"] == ["a@b.com"]
        assert result["phone"] == []

    def test_markdown_wrapped_json(self) -> None:
        text = '```json\n{"email": ["x@y.com"]}\n```'
        result = _clean_json(text)
        assert result is not None
        assert result["email"] == ["x@y.com"]

    def test_markdown_no_language(self) -> None:
        text = '```\n{"website": ["https://example.com"]}\n```'
        result = _clean_json(text)
        assert result is not None
        assert result["website"] == ["https://example.com"]

    def test_invalid_json_returns_none(self) -> None:
        assert _clean_json("this is not json") is None

    def test_empty_string_returns_none(self) -> None:
        assert _clean_json("") is None

    def test_nested_json(self) -> None:
        text = '{"email": [], "notes": "Company founded in 2020"}'
        result = _clean_json(text)
        assert result is not None
        assert result["notes"] == "Company founded in 2020"

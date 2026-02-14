"""Tests for services.data_loader module."""

from __future__ import annotations

from unittest.mock import patch

from services.data_loader import get_buyer_names, get_countries, load_buyers


class TestLoadBuyers:
    """Tests for the load_buyers function."""

    def test_load_valid_json(self, temp_data_file: str) -> None:
        """load_buyers returns list of dicts for valid JSON."""
        with patch("services.data_loader.DATA_PATH", temp_data_file):
            load_buyers.clear()  # Clear st.cache_data
            result = load_buyers()

        assert result is not None
        assert len(result) == 3
        assert result[0]["buyer_name"] == "Test Corp Alpha"

    def test_load_missing_file(self, tmp_path) -> None:
        """load_buyers returns None when file doesn't exist."""
        fake_path = str(tmp_path / "nonexistent.json")
        with patch("services.data_loader.DATA_PATH", fake_path):
            load_buyers.clear()
            result = load_buyers()

        assert result is None

    def test_load_corrupt_json(self, empty_data_file: str) -> None:
        """load_buyers returns None for invalid JSON."""
        with open(empty_data_file, "w") as f:
            f.write("{invalid json content")

        with patch("services.data_loader.DATA_PATH", empty_data_file):
            load_buyers.clear()
            result = load_buyers()

        assert result is None

    def test_load_empty_array(self, tmp_path) -> None:
        """load_buyers returns empty list for empty JSON array."""
        path = tmp_path / "empty.json"
        path.write_text("[]", encoding="utf-8")

        with patch("services.data_loader.DATA_PATH", str(path)):
            load_buyers.clear()
            result = load_buyers()

        assert result == []


class TestGetBuyerNames:
    """Tests for get_buyer_names helper."""

    def test_returns_sorted_names(self, sample_buyers) -> None:
        names = get_buyer_names(sample_buyers)
        assert names == ["Beta Industries", "Gamma Trading", "Test Corp Alpha"]

    def test_returns_empty_for_none(self) -> None:
        assert get_buyer_names(None) == []

    def test_returns_empty_for_empty_list(self) -> None:
        assert get_buyer_names([]) == []

    def test_skips_empty_names(self) -> None:
        data = [{"buyer_name": ""}, {"buyer_name": "Valid"}]
        assert get_buyer_names(data) == ["Valid"]


class TestGetCountries:
    """Tests for get_countries helper."""

    def test_returns_sorted_countries(self, sample_buyers) -> None:
        countries = get_countries(sample_buyers)
        assert countries == ["Germany", "Japan", "United States"]

    def test_returns_empty_for_none(self) -> None:
        assert get_countries(None) == []

    def test_skips_empty_countries(self) -> None:
        data = [{"country_english": ""}, {"country_english": "France"}]
        assert get_countries(data) == ["France"]

"""Comprehensive tests for config module."""
import pytest
from backend.config import Settings, settings


class TestSettings:
    """Test Settings dataclass."""

    def test_settings_has_app_name(self):
        s = Settings()
        assert s.app_name == "XinAn-Med-GraphRAG"

    def test_settings_has_version(self):
        s = Settings()
        assert s.version == "0.1.0"

    def test_settings_has_port(self):
        s = Settings()
        assert s.port == 8024

    def test_settings_custom_values(self):
        s = Settings(app_name="Test", version="1.0.0", port=9000)
        assert s.app_name == "Test"
        assert s.version == "1.0.0"
        assert s.port == 9000

    def test_settings_singleton(self):
        assert settings.app_name == "XinAn-Med-GraphRAG"
        assert settings.version == "0.1.0"
        assert settings.port == 8024

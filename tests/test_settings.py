"""Tests for application settings."""

import os
import pytest
from pathlib import Path
from tempfile import gettempdir
import unittest.mock as mock

from lakewatch.settings import Settings, LogLevel


def test_default_settings() -> None:
    """Test default settings values."""
    # Create a clean settings instance without environment variable influence
    with mock.patch.dict(os.environ, {}, clear=True):
        settings = Settings()

        # Check default values
        assert settings.host == "127.0.0.1"  # Updated to match actual default
        assert settings.port == 8000
        assert settings.workers_count == 1
        assert settings.reload is False
        assert settings.environment == "dev"
        assert settings.log_level == LogLevel.INFO
        assert settings.db_file == Path(gettempdir()) / "db.sqlite3"
        assert settings.db_echo is False

        # Check RabbitMQ defaults
        assert settings.rabbitmq_host == "localhost"
        assert settings.rabbitmq_port == 5672
        assert settings.rabbitmq_queue == "node_data"

        # Check threshold defaults
        assert settings.temperature_threshold == 30.0
        assert settings.humidity_threshold == 70.0
        assert settings.ph_threshold == 7.0
        assert settings.turbidity_threshold == 100.0
        assert settings.conductivity_threshold == 100.0
        assert settings.oxygen_threshold == 5.0


def test_environment_override() -> None:
    """Test settings override from environment variables."""
    with mock.patch.dict(
        os.environ,
        {
            "LAKEWATCH_HOST": "0.0.0.0",
            "LAKEWATCH_PORT": "9000",
            "LAKEWATCH_WORKERS_COUNT": "4",
            "LAKEWATCH_RELOAD": "true",
            "LAKEWATCH_LOG_LEVEL": "DEBUG",
            "LAKEWATCH_RABBITMQ_HOST": "rabbitmq.example.com",
            "LAKEWATCH_TEMPERATURE_THRESHOLD": "25.5",
        },
    ):
        settings = Settings()

        # Check overridden values
        assert settings.host == "0.0.0.0"
        assert settings.port == 9000
        assert settings.workers_count == 4
        assert settings.reload is True
        assert settings.log_level == LogLevel.DEBUG
        assert settings.rabbitmq_host == "rabbitmq.example.com"
        assert settings.temperature_threshold == 25.5

        # Other values should remain default
        assert settings.rabbitmq_port == 5672
        assert settings.ph_threshold == 7.0


def test_log_level_enum() -> None:
    """Test the LogLevel enum."""
    # Verify all expected log levels are defined
    assert LogLevel.NOTSET == "NOTSET"
    assert LogLevel.DEBUG == "DEBUG"
    assert LogLevel.INFO == "INFO"
    assert LogLevel.WARNING == "WARNING"
    assert LogLevel.ERROR == "ERROR"
    assert LogLevel.FATAL == "FATAL"

    # Test conversion from string
    assert LogLevel("DEBUG") == LogLevel.DEBUG
    assert LogLevel("INFO") == LogLevel.INFO

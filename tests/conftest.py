"""Shared fixtures for all tests."""

import pytest
import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from typing import Dict, Tuple, Generator, Any

from lakewatch.web.application import get_app
from lakewatch.settings import Settings


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the app."""
    return TestClient(get_app())


@pytest.fixture
def temp_db_path() -> Generator[Path, None, None]:
    """Create a temporary database file path."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite3") as temp_file:
        yield Path(temp_file.name)


@pytest.fixture
def mock_settings(temp_db_path: Path) -> Generator[MagicMock, None, None]:
    """Create mock application settings for testing."""
    with patch("lakewatch.settings.settings") as mock_settings_obj:
        mock_settings_obj.db_file = temp_db_path
        mock_settings_obj.host = "127.0.0.1"
        mock_settings_obj.port = 8000
        mock_settings_obj.workers_count = 1
        mock_settings_obj.rabbitmq_host = "localhost"
        mock_settings_obj.rabbitmq_port = 5672
        mock_settings_obj.rabbitmq_queue = "node_data"
        mock_settings_obj.temperature_threshold = 30.0
        mock_settings_obj.ph_threshold = 7.0
        mock_settings_obj.oxygen_threshold = 5.0
        yield mock_settings_obj


@pytest.fixture
def mock_node_data() -> Dict[str, Any]:
    """Create mock node data for tests."""
    timestamp = int(datetime.now().timestamp())
    return {
        "node_id": "test_node",
        "timestamp": timestamp,
        "latitude": 12.345,
        "longitude": 67.890,
        "temperature": 25.0,
        "ph": 7.0,
        "dissolved_oxygen": 8.0,
        "maintenance_required": 0,
    }


@pytest.fixture
def mock_db_connection() -> Generator[Tuple[MagicMock, MagicMock], None, None]:
    """Create a mock SQLite database connection."""
    with patch("sqlite3.connect") as mock_connect:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        yield mock_conn, mock_cursor


@pytest.fixture
def mock_websocket() -> AsyncMock:
    """Create a mock WebSocket connection."""
    mock_ws = AsyncMock()
    mock_ws.send_text = AsyncMock()
    mock_ws.receive_text = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.close = AsyncMock()
    return mock_ws

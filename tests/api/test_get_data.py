"""Tests for the get_data API endpoint."""

import json
import pytest
import sqlite3
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from typing import List, Dict, Any

from lakewatch.web.application import get_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the app."""
    return TestClient(get_app())


@pytest.fixture
def mock_db_data() -> List[Dict[str, str]]:
    """Create mock data for database responses."""
    return [
        {"node_id": "node1", "data": json.dumps({"temperature": 25.6, "pH": 7.2})},
        {"node_id": "node1", "data": json.dumps({"temperature": 25.8, "pH": 7.3})},
    ]


def test_get_data_success(
    client: TestClient, mock_db_data: List[Dict[str, str]]
) -> None:
    """Test successful data retrieval for a node."""
    with patch("sqlite3.connect") as mock_connect:
        # Set up the mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock fetchall to return our test data
        mock_cursor.fetchall.return_value = mock_db_data

        # Make the request
        response = client.get("/api/get_data/node1")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["node_id"] == "node1"
        assert data["count"] == 2
        assert len(data["data"]) == 2


def test_get_data_no_results(client: TestClient) -> None:
    """Test when no data is found for a node."""
    with patch("sqlite3.connect") as mock_connect:
        # Set up the mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchall to return empty results
        mock_cursor.fetchall.return_value = []

        # Make the request
        response = client.get("/api/get_data/nonexistent_node")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["node_id"] == "nonexistent_node"
        assert data["message"] == "No data found for the last 24 hours"
        assert data["data"] == []


def test_get_data_db_error(client: TestClient) -> None:
    """Test database error handling."""
    with patch("sqlite3.connect") as mock_connect:
        # Set up the mock to raise an error
        mock_connect.side_effect = sqlite3.Error("Test database error")

        # Make the request
        response = client.get("/api/get_data/node1")

        # Verify the response
        assert response.status_code == 500
        data = response.json()
        assert "Database error" in data["detail"]

"""Tests for the get_nodes API endpoint."""

import pytest
import sqlite3
from datetime import datetime
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from typing import List, Dict, Any

from lakewatch.web.application import get_app


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the app."""
    return TestClient(get_app())


@pytest.fixture
def mock_node_data() -> List[Dict[str, Any]]:
    """Create mock data for node metadata responses."""
    timestamp = int(datetime.now().timestamp())
    return [
        {
            "node_id": "node1",
            "last_updated": timestamp,
            "latitude": 12.345,
            "longitude": 67.890,
            "temperature": 25.6,
            "ph": 7.2,
            "dissolved_oxygen": 8.5,
            "maintenance_required": 0,
        },
        {
            "node_id": "node2",
            "last_updated": timestamp,
            "latitude": 23.456,
            "longitude": 78.901,
            "temperature": 26.3,
            "ph": 6.9,
            "dissolved_oxygen": 7.8,
            "maintenance_required": 1,
        },
    ]


def test_get_nodes_success(
    client: TestClient, mock_node_data: List[Dict[str, Any]]
) -> None:
    """Test successful retrieval of all nodes."""
    with patch("sqlite3.connect") as mock_connect:
        # Set up the mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock fetchall to return our test data
        mock_cursor.fetchall.return_value = mock_node_data

        # Make the request
        response = client.get("/api/get_nodes/")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["data"]) == 2

        # Verify node details
        assert data["data"][0]["node_id"] == "node1"
        assert data["data"][1]["node_id"] == "node2"
        assert "datetime" in data["data"][0]
        assert data["data"][1]["maintenance_required"] == 1


def test_get_nodes_no_results(client: TestClient) -> None:
    """Test when no nodes are found."""
    with patch("sqlite3.connect") as mock_connect:
        # Set up the mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        # Mock fetchall to return empty results
        mock_cursor.fetchall.return_value = []

        # Make the request
        response = client.get("/api/get_nodes/")

        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "No nodes found"


def test_get_nodes_db_error(client: TestClient) -> None:
    """Test database error handling."""
    with patch("sqlite3.connect") as mock_connect:
        # Set up the mock to raise an error
        mock_connect.side_effect = sqlite3.Error("Test database error")

        # Make the request
        response = client.get("/api/get_nodes/")

        # Verify the response
        assert response.status_code == 500
        data = response.json()
        assert "Database error" in data["detail"]


def test_get_nodes_key_error_handling(client: TestClient) -> None:
    """Test handling of malformed data in the database."""
    with patch("sqlite3.connect") as mock_connect:
        # Set up the mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Create malformed data (missing keys)
        malformed_data = [
            {"node_id": "node1"},  # Missing required fields
            {
                "node_id": "node2",
                "last_updated": int(datetime.now().timestamp()),
                "latitude": 23.456,
                "longitude": 78.901,
                "temperature": 26.3,
                "ph": 6.9,
                "dissolved_oxygen": 7.8,
                "maintenance_required": 1,
            },
        ]

        mock_cursor.fetchall.return_value = malformed_data

        # Make the request
        response = client.get("/api/get_nodes/")

        # Verify the response - should only include valid node (node2)
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1  # Only one valid node
        assert len(data["data"]) == 1
        assert data["data"][0]["node_id"] == "node2"

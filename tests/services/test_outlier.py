"""Tests for the outlier detection service."""

import pytest
import sqlite3
from unittest.mock import patch, MagicMock, AsyncMock
import json
from typing import List, Tuple

from lakewatch.services.outlier import process_outliers


@pytest.fixture
def mock_db_readings() -> List[Tuple[float, float, float]]:
    """Create mock historical readings for testing outlier detection."""
    return [
        (25.0, 7.0, 8.0),  # temperature, pH, dissolved_oxygen
        (25.2, 7.1, 7.9),
        (24.9, 6.9, 8.1),
        (25.3, 7.0, 8.0),
        (25.1, 7.2, 7.8),
    ]


@pytest.mark.asyncio
async def test_process_outliers_no_outliers() -> None:
    """Test normal data processing with no outliers."""
    with patch("sqlite3.connect") as mock_connect, patch(
        "lakewatch.services.outlier.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Set up database mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock historical readings (normal range)
        mock_cursor.fetchall.return_value = [
            (25.0, 7.0, 8.0),
            (25.2, 7.1, 7.9),
            (24.9, 6.9, 8.1),
            (25.3, 7.0, 8.0),
            (25.1, 7.2, 7.8),
        ]

        # Create a payload with values within normal range
        payload = {
            "node_id": "node1",
            "temperature": 25.2,
            "ph": 7.1,
            "dissolved_oxygen": 8.0,
        }

        # Process the data
        await process_outliers(payload)

        # Verify no alerts were sent
        mock_send_alert.assert_not_called()


@pytest.mark.asyncio
async def test_process_outliers_temperature_outlier() -> None:
    """Test outlier detection for temperature values."""
    with patch("sqlite3.connect") as mock_connect, patch(
        "lakewatch.services.outlier.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Set up database mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock historical readings
        mock_cursor.fetchall.return_value = [
            (25.0, 7.0, 8.0),
            (25.2, 7.1, 7.9),
            (24.9, 6.9, 8.1),
            (25.3, 7.0, 8.0),
            (25.1, 7.2, 7.8),
        ]

        # Create a payload with an outlier temperature
        payload = {
            "node_id": "node1",
            "temperature": 30.0,  # Significant outlier
            "ph": 7.1,
            "dissolved_oxygen": 8.0,
        }

        # Process the data
        await process_outliers(payload)

        # Verify temperature alert was sent
        mock_send_alert.assert_called_once()


@pytest.mark.asyncio
async def test_process_outliers_multiple_outliers() -> None:
    """Test detection of multiple outliers in one payload."""
    with patch("sqlite3.connect") as mock_connect, patch(
        "lakewatch.services.outlier.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Set up database mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock historical readings
        mock_cursor.fetchall.return_value = [
            (25.0, 7.0, 8.0),
            (25.2, 7.1, 7.9),
            (24.9, 6.9, 8.1),
            (25.3, 7.0, 8.0),
            (25.1, 7.2, 7.8),
        ]

        # Create a payload with multiple outliers
        payload = {
            "node_id": "node1",
            "temperature": 30.0,  # Temperature outlier
            "ph": 5.0,  # pH outlier
            "dissolved_oxygen": 8.0,
        }

        # Process the data
        await process_outliers(payload)

        # Verify that multiple alerts were sent (one for each outlier)
        assert mock_send_alert.call_count == 2


@pytest.mark.asyncio
async def test_process_outliers_insufficient_history() -> None:
    """Test handling when there's not enough historical data."""
    with patch("sqlite3.connect") as mock_connect, patch(
        "lakewatch.services.outlier.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Set up database mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Mock insufficient historical readings
        mock_cursor.fetchall.return_value = [
            (25.0, 7.0, 8.0),  # Only one reading
        ]

        # Create a payload with an outlier
        payload = {
            "node_id": "node1",
            "temperature": 30.0,
            "ph": 5.0,
            "dissolved_oxygen": 4.0,
        }

        # Process the data
        await process_outliers(payload)

        # Verify no alerts were sent due to insufficient history
        mock_send_alert.assert_not_called()


@pytest.mark.asyncio
async def test_process_outliers_db_error() -> None:
    """Test handling of database errors."""
    with patch("sqlite3.connect") as mock_connect, patch(
        "lakewatch.services.outlier.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Set up database mock to raise an exception
        mock_connect.side_effect = sqlite3.Error("Test database error")

        payload = {
            "node_id": "node1",
            "temperature": 25.0,
            "ph": 7.0,
            "dissolved_oxygen": 8.0,
        }

        # Process should handle the exception gracefully
        await process_outliers(payload)

        # No alerts should be sent
        mock_send_alert.assert_not_called()

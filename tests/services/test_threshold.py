"""Tests for the threshold service."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from lakewatch.services.threshold import threshold_check


@pytest.mark.asyncio
async def test_threshold_check_no_thresholds_exceeded() -> None:
    """Test when no thresholds are exceeded."""
    with patch("lakewatch.services.threshold.settings") as mock_settings, patch(
        "lakewatch.services.threshold.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Configure threshold settings
        mock_settings.temperature_threshold = 30.0
        mock_settings.ph_threshold = 8.0
        mock_settings.oxygen_threshold = 10.0

        # Create a payload with values below thresholds
        payload = {
            "node_id": "node1",
            "latitude": 12.345,
            "longitude": 67.890,
            "timestamp": 1620000000,
            "temperature": 25.0,
            "ph": 7.0,
            "dissolved_oxygen": 8.0,
            "maintenance_required": 0,
        }

        # Process the data
        await threshold_check(payload)

        # Verify no alerts were sent
        mock_send_alert.assert_not_called()


@pytest.mark.asyncio
async def test_threshold_check_temperature_exceeded() -> None:
    """Test when temperature threshold is exceeded."""
    with patch("lakewatch.services.threshold.settings") as mock_settings, patch(
        "lakewatch.services.threshold.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Configure threshold settings
        mock_settings.temperature_threshold = 25.0
        mock_settings.ph_threshold = 8.0
        mock_settings.oxygen_threshold = 10.0

        # Create a payload with temperature exceeding threshold
        payload = {
            "node_id": "node1",
            "latitude": 12.345,
            "longitude": 67.890,
            "timestamp": 1620000000,
            "temperature": 26.0,  # Above threshold
            "ph": 7.0,
            "dissolved_oxygen": 8.0,
            "maintenance_required": 0,
        }

        # Process the data
        await threshold_check(payload)

        # Verify temperature alert was sent
        mock_send_alert.assert_called_once()
        args = mock_send_alert.call_args[1]
        assert "Temperature threshold exceeded" in args["message"]
        assert "26.0" in args["message"]


@pytest.mark.asyncio
async def test_threshold_check_multiple_thresholds_exceeded() -> None:
    """Test when multiple thresholds are exceeded."""
    with patch("lakewatch.services.threshold.settings") as mock_settings, patch(
        "lakewatch.services.threshold.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Configure threshold settings
        mock_settings.temperature_threshold = 25.0
        mock_settings.ph_threshold = 7.0
        mock_settings.oxygen_threshold = 8.0

        # Create a payload with multiple thresholds exceeded
        payload = {
            "node_id": "node1",
            "latitude": 12.345,
            "longitude": 67.890,
            "timestamp": 1620000000,
            "temperature": 26.0,  # Above threshold
            "ph": 7.5,  # Above threshold
            "dissolved_oxygen": 9.0,  # Above threshold
            "maintenance_required": 0,
        }

        # Process the data
        await threshold_check(payload)

        # Verify that multiple alerts were sent (one for each threshold exceeded)
        assert mock_send_alert.call_count == 3


@pytest.mark.asyncio
async def test_threshold_check_maintenance_required() -> None:
    """Test when maintenance is required."""
    with patch("lakewatch.services.threshold.settings") as mock_settings, patch(
        "lakewatch.services.threshold.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Configure threshold settings
        mock_settings.temperature_threshold = 30.0
        mock_settings.ph_threshold = 8.0
        mock_settings.oxygen_threshold = 10.0

        # Create a payload indicating maintenance is required
        payload = {
            "node_id": "node1",
            "latitude": 12.345,
            "longitude": 67.890,
            "timestamp": 1620000000,
            "temperature": 25.0,
            "ph": 7.0,
            "dissolved_oxygen": 8.0,
            "maintenance_required": 1,  # Maintenance required
        }

        # Process the data
        await threshold_check(payload)

        # Verify maintenance alert was sent
        mock_send_alert.assert_called_once()
        args = mock_send_alert.call_args[1]
        assert "Maintenance required" in args["message"]
        assert "node1" in args["message"]
        assert "(12.345, 67.89)" in args["message"]


@pytest.mark.asyncio
async def test_threshold_check_missing_values() -> None:
    """Test handling of payloads with missing sensor values."""
    with patch("lakewatch.services.threshold.settings") as mock_settings, patch(
        "lakewatch.services.threshold.send_threshold_alert", return_value=True
    ) as mock_send_alert:

        # Configure threshold settings
        mock_settings.temperature_threshold = 25.0
        mock_settings.ph_threshold = 7.0
        mock_settings.oxygen_threshold = 8.0

        # Create a payload with missing values
        payload = {
            "node_id": "node1",
            "latitude": 12.345,
            "longitude": 67.890,
            "timestamp": 1620000000,
            # No temperature
            "ph": 7.5,  # Above threshold
            # No dissolved_oxygen
            "maintenance_required": 0,
        }

        # Process the data
        await threshold_check(payload)

        # Verify that only one alert was sent (for pH)
        mock_send_alert.assert_called_once()
        args = mock_send_alert.call_args[1]
        assert "pH threshold exceeded" in args["message"]

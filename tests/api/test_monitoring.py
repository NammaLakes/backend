"""Tests for the monitoring WebSocket API."""

import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
from unittest.mock import patch, MagicMock, AsyncMock

from lakewatch.web.application import get_app
from lakewatch.web.api.monitoring.views import connections, send_threshold_alert


@pytest.fixture
def client() -> TestClient:
    """Create a test client for the app."""
    return TestClient(get_app())


def test_websocket_connect(client: TestClient) -> None:
    """Test WebSocket connection is established."""
    with client.websocket_connect("/api/monitoring/ws") as websocket:
        # Just testing that connection succeeds
        pass


@pytest.mark.asyncio
async def test_send_threshold_alert_with_connections() -> None:
    """Test sending threshold alert to active connections."""
    # Mock a WebSocket connection
    mock_ws = AsyncMock()

    # Store the mock in connections set
    connections.clear()  # Clear any existing connections
    connections.add(mock_ws)

    # Send an alert
    await send_threshold_alert("Test alert message")

    # Verify the message was sent
    mock_ws.send_text.assert_called_once_with("Test alert message")


@pytest.mark.asyncio
async def test_send_threshold_alert_no_connections() -> None:
    """Test sending threshold alert when there are no connections."""
    # Clear all connections
    connections.clear()

    # Send an alert (should not raise exceptions)
    await send_threshold_alert("Test alert message")


@pytest.mark.asyncio
async def test_send_threshold_alert_with_exception() -> None:
    """Test handling exceptions when sending threshold alert."""
    # Mock a WebSocket connection that raises an exception
    mock_ws = AsyncMock()
    mock_ws.send_text.side_effect = Exception("Connection error")

    # Store the mock in connections set
    connections.clear()
    connections.add(mock_ws)

    # Send an alert
    await send_threshold_alert("Test alert message")

    # Verify the connection was removed due to the exception
    assert len(connections) == 0

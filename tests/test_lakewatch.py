"""Basic tests for the Lakewatch application."""

import pytest
from fastapi.testclient import TestClient

from lakewatch.web.application import get_app


def test_app_creates() -> None:
    """Test that the application instance can be created."""
    app = get_app()
    assert app is not None


def test_api_router_configured() -> None:
    """Test that the API router is configured with the expected routes."""
    app = get_app()
    client = TestClient(app)

    # Check API documentation endpoints are available
    response = client.get("/api/docs")
    assert response.status_code == 200

    response = client.get("/api/openapi.json")
    assert response.status_code == 200

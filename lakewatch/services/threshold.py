from loguru import logger
from typing import Dict, Any

from lakewatch.settings import settings
from lakewatch.web.api.monitoring.views import send_threshold_alert


async def threshold_check(payload: Dict[str, Any]) -> None:
    """
    Check if sensor readings exceed threshold values and send alerts if needed.

    Args:
        payload: Dictionary containing sensor data with node information and readings
    """
    # Extract the node information
    node_id = payload.get("node_id")
    latitude = payload.get("latitude")
    longitude = payload.get("longitude")
    timestamp = payload.get("timestamp")

    if (
        "temperature" in payload
        and payload["temperature"] > settings.temperature_threshold
    ):
        await send_threshold_alert(
            message=f"Temperature threshold exceeded: {payload['temperature']}"
        )
        logger.info(
            f"Node {node_id}: Temperature threshold exceeded: {payload['temperature']}"
        )

    if "ph" in payload and payload["ph"] > settings.ph_threshold:
        await send_threshold_alert(message=f"pH threshold exceeded: {payload['ph']}")
        logger.info(f"Node {node_id}: pH threshold exceeded: {payload['ph']}")

    if (
        "dissolved_oxygen" in payload
        and payload["dissolved_oxygen"] > settings.oxygen_threshold
    ):
        await send_threshold_alert(
            message=f"Oxygen threshold exceeded: {payload['dissolved_oxygen']}"
        )
        logger.info(
            f"Node {node_id}: Oxygen threshold exceeded: {payload['dissolved_oxygen']}"
        )

    # Check if maintenance is required
    if payload.get("maintenance_required", 0) == 1:
        await send_threshold_alert(
            message=f"Maintenance required for node {node_id} at location ({latitude}, {longitude})"
        )
        logger.warning(f"Maintenance required for node {node_id}")

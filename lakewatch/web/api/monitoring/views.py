from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import asyncio
import json
from loguru import logger
from typing import Set, Dict, Any
from datetime import datetime

router = APIRouter()

connections: Set[WebSocket] = set()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    connections.add(websocket)
    logger.info("Client connected via WebSocket")

    try:
        while True:
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        connections.remove(websocket)
        logger.info("Client disconnected")


async def send_threshold_alert(message: str) -> None:
    if not connections:
        logger.warning("No active clients to send the alert.")
        return

    logger.info(f"Sending alert to clients: {message}")
    for connection in list(connections):
        try:
            await connection.send_text(message)
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            connections.remove(connection)


async def broadcast_sensor_reading(node_id: str, timestamp: datetime, payload: Dict[str, Any]):
    """Broadcasts a sensor reading JSON to all connected WebSocket clients."""
    # Format the timestamp as an ISO string (common practice for JS)
    timestamp_iso = timestamp.isoformat()
    message_data = {
        "node_id": node_id,
        "timestamp": timestamp_iso,
        "payload": payload  # Assuming payload is already a dict like {'temperature': ..., 'pH': ..., ...}
    }
    message_json = json.dumps(message_data)
    logger.debug(f"Broadcasting sensor reading: {message_json}")

    disconnected_clients = set()
    for connection in list(connections):  # Iterate over a copy for safe removal
        try:
            await connection.send_text(message_json)
        except WebSocketDisconnect:
            disconnected_clients.add(connection)
            logger.info(f"Client disconnected: {connection.client}")
        except Exception as e:  # Catch other potential errors during send
            disconnected_clients.add(connection)
            logger.error(f"Error sending to client {connection.client}: {e}")

    # Clean up disconnected clients from the main set
    for client in disconnected_clients:
        connections.discard(client)

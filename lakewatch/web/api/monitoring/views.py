from fastapi import WebSocket, APIRouter, WebSocketDisconnect
import asyncio
from loguru import logger

router = APIRouter()

connections = set()


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

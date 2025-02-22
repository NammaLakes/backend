from fastapi import WebSocket, WebSocketDisconnect
from lakewatch.web.api.auth import validate_api_key

connected_clients = []

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    api_key = websocket.headers.get("X-API-Key")
    
    if not api_key or not validate_api_key(api_key):
        await websocket.close(code=1008)
        return

    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

async def send_alert(alert_message: str):
    for client in connected_clients:
        await client.send_text(alert_message)

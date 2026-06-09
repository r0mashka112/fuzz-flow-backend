from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket.manager import web_socket_manager

router = APIRouter(prefix="/websocket", tags=["websocket"])


@router.websocket("/", name="Websocket")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket connection for real-time dashboard updates"""
    await web_socket_manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        web_socket_manager.disconnect(websocket)

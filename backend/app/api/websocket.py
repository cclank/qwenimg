"""WebSocket API路由 - 实时通信"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import logging

from ..tasks import manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket连接端点"""
    await manager.connect(websocket, session_id)
    try:
        # 发送欢迎消息
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "WebSocket连接成功"
        })

        # 保持连接，接收客户端消息
        while True:
            data = await websocket.receive_json()
            logger.info(f"Received from {session_id}: {data}")

            # 处理客户端消息（如ping/pong心跳）
            if data.get("type") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                })

    except WebSocketDisconnect:
        manager.disconnect(session_id)
        logger.info(f"Client {session_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for {session_id}: {e}")
        manager.disconnect(session_id)

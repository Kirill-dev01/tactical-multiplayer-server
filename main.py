from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json

app = FastAPI()

# --- 1. THE GAME ROOM MANAGER ---
class ConnectionManager:
    def __init__(self):
        # A Dictionary to hold multiple isolated private rooms
        self.rooms: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room_id: str):
        await websocket.accept()
        if room_id not in self.rooms:
            self.rooms[room_id] = []
            
        self.rooms[room_id].append(websocket)
        print(f"SYS_LOG: Commander joined Room {room_id}. Total: {len(self.rooms[room_id])}")

    def disconnect(self, websocket: WebSocket, room_id: str):
        if room_id in self.rooms:
            self.rooms[room_id].remove(websocket)
            if len(self.rooms[room_id]) == 0:
                del self.rooms[room_id]  # Clean up empty rooms from memory

    async def broadcast(self, message: str, room_id: str):
        # Only broadcast moves to players in this EXACT room
        if room_id in self.rooms:
            for connection in self.rooms[room_id]:
                await connection.send_text(message)

manager = ConnectionManager()

# --- THE GAME ROOM ENDPOINT ---
@app.websocket("/ws/match/{room_id}")
async def match_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)
        # Broadcast the drop-out to the remaining players in the ACTIVE ROOM!
        disconnect_msg = json.dumps({"action": "PLAYER_LEFT"})
        await manager.broadcast(disconnect_msg, room_id)
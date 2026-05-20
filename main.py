from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List, Dict
import json
import uuid

app = FastAPI()

# --- 1. THE GAME ROOM MANAGER ---
class ConnectionManager:
    def __init__(self):
        # We upgraded this to a Dictionary to hold multiple isolated rooms!
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
                del self.rooms[room_id] # Clean up empty rooms

    async def broadcast(self, message: str, room_id: str):
        # Only broadcast moves to players in this EXACT room
        if room_id in self.rooms:
            for connection in self.rooms[room_id]:
                await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/match/{room_id}")
async def match_endpoint(websocket: WebSocket, room_id: str):
    await manager.connect(websocket, room_id)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(data, room_id)
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_id)


# --- 2. THE PUBLIC MATCHMAKER ---
class Matchmaker:
    def __init__(self):
        self.queue: List[WebSocket] = []

    async def search(self, websocket: WebSocket):
        await websocket.accept()
        self.queue.append(websocket)
        print(f"SYS_LOG: Player entered public queue. Waiting: {len(self.queue)}")

        # If 2 players are waiting, pair them up!
        if len(self.queue) >= 2:
            p1 = self.queue.pop(0)
            p2 = self.queue.pop(0)
            
            # Generate a secure, random 6-character room code
            room_id = f"PUB-{uuid.uuid4().hex[:6].upper()}"
            
            # Send the code to both players
            payload = json.dumps({"action": "MATCH_FOUND", "room_id": room_id})
            await p1.send_text(payload)
            await p2.send_text(payload)
            
            # Boot them from the queue so React can connect them to the real room
            await p1.close()
            await p2.close()

matchmaker = Matchmaker()

@app.websocket("/ws/matchmake")
async def matchmake_endpoint(websocket: WebSocket):
    await matchmaker.search(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in matchmaker.queue:
            matchmaker.queue.remove(websocket)
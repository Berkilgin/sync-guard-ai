from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import json
import os
from ai_engine import resolve_sync_conflict

app = FastAPI()

app.mount("/static", StaticFiles(directory="public"), name="static")

@app.get("/")
async def get_index():
    with open("public/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        self.current_text = ""

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        # Yeni bağlananlara sadece metni gönder (ilk açılışta JSON hatası almamak için)
        if self.current_text:
            init_data = json.dumps({"resolved_text": self.current_text, "action_log": "Joined workspace."})
            await websocket.send_text(init_data)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# Sadece websocket_endpoint fonksiyonunu şu şekilde güncellemen yeterli:
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Gelen JSON verisini ayrıştırıp kullanıcı adını ve metni ayırıyoruz
            try:
                payload = json.loads(data)
                user_text = payload.get("text", "")
                username = payload.get("username", "Unknown User")
            except:
                user_text = data
                username = "System"
            
            # Kullanıcı adını da AI fonksiyonuna gönderiyoruz
            ai_result = resolve_sync_conflict(manager.current_text, user_text, username)
            manager.current_text = ai_result["resolved_text"]
            
            await manager.broadcast(json.dumps(ai_result))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


if __name__ == "__main__":
    # Port numarasını çevreden (environment) al, yoksa 8000 kullan
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
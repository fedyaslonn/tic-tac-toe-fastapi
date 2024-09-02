from fastapi import FastAPI, WebSocket, status, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
import sys
import os
from starlette.websockets import WebSocketDisconnect
from starlette.requests import Request
from fastapi.responses import HTMLResponse
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from .utils import game, manager

templates_path = Path(__file__).resolve().parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_path))

router = APIRouter()

@router.get("/tictac")
async def get(request: Request):
    file_path = templates_path / "index.html"
    with open(file_path, 'r') as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            data = json.loads(data)
            result = await game.make_move(manager, data)
            await manager.broadcast(result)
    except WebSocketDisconnect:
        await manager.disconnect(websocket)
    except Exception as e:
        print(f"Ошибка: {e}")
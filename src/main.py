from fastapi import FastAPI, WebSocket, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import json
from starlette.websockets import WebSocketDisconnect
import sys
import os
from server.router import router as server_router
print(sys.path)

app = FastAPI()


app.include_router(server_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
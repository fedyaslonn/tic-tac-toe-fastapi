import json
import random
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import List

class Game:
    def __init__(self):
        self.board = [None] * 9
        self.current_turn = None

    def reset_board(self):
        self.board = [None] * 9

    def is_draw(self):
        if all(cell is not None for cell in self.board):
            self.reset_board()
            return True
        return False


    def is_win(self):
        win_conditions = [
            [0, 1, 2], [3, 4 , 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]
        ]
        for condition in win_conditions:
            if (self.board[condition[0]] is not None and
                    self.board[condition[0]] == self.board[condition[1]] == self.board[condition[2]]):
                self.reset_board()
                return True
        return False


    async def make_move(self, manager, data):
        ind = int(data['cell']) - 1
        data['init'] = False
        if not self.board[ind]:
            self.board[ind] = data['player']
            if self.is_draw():
                data['message'] = "draw"
            elif self.is_win():
                data['message'] = "won"
            else:
                data['message'] = "move"
        else:
            data['message'] = "choose another one"
        await manager.broadcast(data)
        if data['message'] in ['draw', 'won']:
            manager.active_connections = []


game = Game()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.game = game

    async def connect(self, websocket: WebSocket):
        if len(self.active_connections) >= 2:
            await websocket.accept()
            await websocket.close(4000)
        else:
            await websocket.accept()
            self.active_connections.append(websocket)
            if len(self.active_connections) == 1:
                await websocket.send_json({
                    'init': True,
                    'message': 'Ожидание другого игрока',
                })
            else:
                first_player_side = 'X' if random.randint(0, 1) == 0 else 'O'
                second_player_side = 'O' if first_player_side == 'X' else 'X'
                await self.active_connections[1].send_json({
                    'init': True,
                    'player': second_player_side,
                    'message': '',
                })
                await self.active_connections[0].send_json({
                    'init': True,
                    'player': first_player_side,
                    'message': 'Ваш ход!',
                })

    async def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

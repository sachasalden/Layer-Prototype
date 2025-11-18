import asyncio
from shared.protocol import read_messages, send_message, error_message


class BattleEngine:
    def __init__(self):
        self.games = {}
        self.next_game_id = 1

    async def start_battle(self, payload):
        p1 = payload.get("player1")
        p2 = payload.get("player2")

        if not p1 or not p2:
            return error_message(400, "/battle/start", "Missing players")

        game_id = self.next_game_id
        self.next_game_id += 1

        state = {
            "gameId": game_id,
            "turn": p1,
            "players": {
                p1: {"existence": 50, "hand": [], "board": [], "energy": 5},
                p2: {"existence": 50, "hand": [], "board": [], "energy": 5}
            },
            "winner": None
        }

        self.games[game_id] = state

        return {
            "status": 200,
            "resource": "/battle/start",
            "payload": {"gameState": state}
        }

    async def game_state(self, payload):
        game_id = payload.get("gameId")

        state = self.games.get(game_id)
        if not state:
            return error_message(404, "/battle/state", "Game not found")

        return {
            "status": 200,
            "resource": "/battle/state",
            "payload": {"gameState": state}
        }

    async def play_turn(self, payload):
        game_id = payload.get("gameId")
        player = payload.get("player")

        state = self.games.get(game_id)
        if not state:
            return error_message(404, "/battle/turn", "Game not found")

        if state["turn"] != player:
            return error_message(400, "/battle/turn", "Not your turn")

        if state["winner"] is not None:
            return error_message(400, "/battle/turn", "Game already finished")

        opponent = next(x for x in state["players"] if x != player)

        state["players"][player]["energy"] = 5
        state["turn"] = opponent

        return {
            "status": 200,
            "resource": "/battle/turn",
            "payload": {"gameState": state}
        }

    async def attack(self, payload):
        game_id = payload.get("gameId")
        attacker = payload.get("attacker")
        target = payload.get("target")

        state = self.games.get(game_id)
        if not state:
            return error_message(404, "/battle/attack", "Game not found")

        attacker_entity = {"power": 5}  # MOCK
        damage = attacker_entity["power"]

        state["players"][target]["existence"] -= damage

        if state["players"][target]["existence"] <= 0:
            state["winner"] = attacker

        return {
            "status": 200,
            "resource": "/battle/attack",
            "payload": {"gameState": state}
        }

    async def spectator_update(self, payload):
        game_id = payload.get("gameId")

        state = self.games.get(game_id)
        if not state:
            return error_message(404, "/battle/spectate", "Game not found")

        return {
            "status": 200,
            "resource": "/battle/spectate",
            "payload": {"publicGameState": state}
        }

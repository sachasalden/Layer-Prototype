import socket
import json
import time

class HanTTPSessionServer:
    def __init__(self, host="127.0.0.1", port=5000):
        # Server luistert op localhost op poort 5000
        self.host = host
        self.port = port
        self.conn = None     # TCP-verbinding met client
        self.addr = None     # Adres van client

    def start(self):
        # Maak TCP socket aan
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind naar host + port
        s.bind((self.host, self.port))

        # Wacht op inkomende verbindingen (max 1 tegelijk)
        s.listen(1)
        print("Server wacht op verbinding...")

        # Accepteer verbinding met een client
        self.conn, self.addr = s.accept()
        print(f"Verbonden met {self.addr}")

        # Voer handshake uit (start van de sessie)
        self.handle_handshake()

        # Start de sessieloop (heartbeats ontvangen)
        self.session_loop()

    def send_json(self, data: dict):
        # Dictionary -> JSON string -> bytes -> versturen
        msg = json.dumps(data).encode()
        self.conn.sendall(msg)

    def receive_json(self):
        # Ontvang JSON string van client
        data = self.conn.recv(1024).decode()

        # Als er niets binnenkomt, is de verbinding gesloten
        if not data:
            return None

        # JSON string terug naar dict
        return json.loads(data)

    # ----------------------------
    # SESSION LAYER FUNCTIES
    # ----------------------------

    def handle_handshake(self):
        """
        Handshake tussen client en server.
        Client stuurt: { "type": "handshake_init" }
        Server antwoordt: { "type": "handshake_ack" }
        """
        msg = self.receive_json()
        if msg and msg.get("type") == "handshake_init":
            print("Handshake ontvangen.")

            response = {
                "type": "handshake_ack",
                "status": "ok"
            }

            self.send_json(response)
            print("Handshake voltooid.")

    def session_loop(self):
        """
        Blijft continu JSON-berichten ontvangen.
        In deze fase kijken we alleen naar heartbeats.
        """
        print("Sessielaag actief. Wachten op heartbeats...")

        while True:
            msg = self.receive_json()

            # Verbinding gesloten
            if not msg:
                print("Verbinding verbroken.")
                break

            # Heartbeat message
            if msg.get("type") == "heartbeat":
                print("Heartbeat ontvangen.")
                self.send_json({"type": "heartbeat_ack"})


# Start server als script direct wordt uitgevoerd
if __name__ == "__main__":
    server = HanTTPSessionServer()
    server.start()

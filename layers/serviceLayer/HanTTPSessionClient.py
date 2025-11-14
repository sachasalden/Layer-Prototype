import socket
import json
import time

class HanTTPSessionClient:
    def __init__(self, host="127.0.0.1", port=5000):
        # Client maakt verbinding met server via TCP
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self):
        # Maak verbinding met server
        self.sock.connect((self.host, self.port))
        print("Verbonden met server.")

        # Handshake uitvoeren
        self.handshake()

        # Heartbeat-loop starten
        self.heartbeat_loop()

    def send_json(self, data: dict):
        # Dictionary → JSON string → bytes
        msg = json.dumps(data).encode()
        self.sock.sendall(msg)

    def receive_json(self):
        # Wacht op JSON-bericht van server
        data = self.sock.recv(1024).decode()
        if not data:
            return None
        return json.loads(data)

    # ----------------------------
    # SESSION LAYER FUNCTIES
    # ----------------------------

    def handshake(self):
        """
        Client start de handshake.
        Stuurt: { "type": "handshake_init" }
        Wacht op: { "type": "handshake_ack" }
        """

        init_msg = {
            "type": "handshake_init",
            "protocol": "HanTTP",
            "version": 1
        }

        self.send_json(init_msg)

        # Wachten op antwoord
        response = self.receive_json()

        if response and response.get("type") == "handshake_ack":
            print("Handshake succesvol.")
        else:
            print("Handshake mislukt.")

    def heartbeat_loop(self):
        """
        Stuur elke 2 seconden een heartbeat om te controleren
        of de sessie nog actief is.
        """
        print("Heartbeat gestart...")

        while True:
            time.sleep(2)

            # Heartbeat JSON
            self.send_json({"type": "heartbeat"})

            # Wacht op heartbeat bevestiging
            ack = self.receive_json()

            if ack and ack.get("type") == "heartbeat_ack":
                print("Heartbeat bevestigd.")
            else:
                print("Geen heartbeat ACK ontvangen!")
                break


# Start client als dit bestand direct uitgevoerd wordt
if __name__ == "__main__":
    client = HanTTPSessionClient()
    client.connect()

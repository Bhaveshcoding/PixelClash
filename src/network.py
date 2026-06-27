import socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "127.0.0.1"  # Target Address (Localhost for local testing)
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p_id = self.connect()

    def connect(self) -> int:
        """Establishes connection to the server and retrieves a unique player ID."""
        try:
            self.client.connect(self.addr)
            # Read back assigned text ID integer token
            assigned_id = self.client.recv(1048).decode()
            print(f"[NETWORK INFO] Connected to server. Assigned ID: {assigned_id}")
            return int(assigned_id)
        except Exception as e:
            print(f"[NETWORK ERROR] Failed to connect to game server: {e}")
            return -1

    def send_and_receive(self, data: dict) -> dict:
        """Transmits local coordinates and receives the full server state."""
        try:
            # Serialize local state to a byte stream and push across the socket
            self.client.send(pickle.dumps(data))
            
            # Receive back the complete serialized lobby dictionary
            raw_response = self.client.recv(4096)
            if not raw_response:
                return {}
            return pickle.loads(raw_response)
        except socket.error as e:
            print(f"[NETWORK ERROR] Frame broadcast exchange failed: {e}")
            return {}

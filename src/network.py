import socket
import pickle

class Network:
    def __init__(self, server_ip="127.0.0.1"):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = server_ip  
        self.port = 5555
        self.addr = (self.server, self.port)
        self.p_id = self.connect()

    def connect(self) -> int:
        try:
            self.client.settimeout(1.0) # <--- ADD THIS LINE (1 second timeout limit)
            self.client.connect(self.addr)
            assigned_id = self.client.recv(1048).decode()
            self.client.settimeout(None) # <--- ADD THIS LINE (Remove timeout for live gameplay)
            return int(assigned_id)
        except Exception:
            return -1


    def send_and_receive(self, data: dict) -> dict:
        try:
            self.client.send(pickle.dumps(data))
            raw_response = self.client.recv(8192) 
            if not raw_response:
                return {}
            return pickle.loads(raw_response)
        except socket.error:
            return {}

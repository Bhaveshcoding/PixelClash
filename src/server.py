import socket
import threading
import pickle

# Server Networking Configuration
SERVER_IP = "0.0.0.0"  # Binds to all available network interfaces
PORT = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind((SERVER_IP, PORT))
except socket.error as e:
    print(f"[ERROR] Server bind failed: {str(e)}")
    exit()

server_socket.listen(4)
print("[SERVER START] Server is running, waiting for connections...")

# Central Database matching client IDs to their active position metrics
# Schema: id: {"x": float, "y": float, "angle": float}
players_state = {}
current_id = 0

def handle_client(conn, player_id):
    """Manages individual client threads for continuous state synchronization."""
    global current_id
    print(f"[CONNECT] Player {player_id} connected successfully.")
    
    # 1. Send the player their unique numerical identity ID upon initial connection
    try:
        conn.send(str(player_id).encode())
    except socket.error as e:
        print(f"[ERROR] Failed to send player ID: {e}")
        conn.close()
        return

    while True:
        try:
            # 2. Receive position updates from the client (buffered at 2048 bytes)
            data = conn.recv(2048)
            if not data:
                print(f"[DISCONNECT] Player {player_id} disconnected cleanly.")
                break
                
            # Decode the incoming positioning data packet
            client_data = pickle.loads(data)
            players_state[player_id] = client_data

            # 3. Compile and broadcast the full lobby state back to the client
            conn.sendall(pickle.dumps(players_state))
            
        except Exception as e:
            print(f"[ERROR] Connection exception with Player {player_id}: {e}")
            break

    # Clean up player state on disconnect
    if player_id in players_state:
        del players_state[player_id]
    conn.close()

while True:
    conn, addr = server_socket.accept()
    print(f"[CONNECTION] Incoming connection received from address: {addr}")
    
    # Spin up an independent background worker thread for each player
    thread = threading.Thread(target=handle_client, args=(conn, current_id), daemon=True)
    thread.start()
    current_id += 1

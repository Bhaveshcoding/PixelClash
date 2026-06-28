import socket
import threading
import pickle
import time
import pygame
from constants import (
    SPAWN_POINTS, MAX_HEALTH, BULLET_DAMAGE, BULLET_SPEED, 
    BULLET_LIFETIME, WALL_LAYOUTS, PLAYER_SIZE, BULLET_SIZE
)

SERVER_IP = "0.0.0.0"
PORT = 5555

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind((SERVER_IP, PORT))
except socket.error as e:
    print(f"[ERROR] Server bind failed: {e}")
    exit()

server_socket.listen(4)
print("[SERVER] Authoritative server running. Waiting for connections...")

# Central Game State Pools
players = {}  # id: {x, y, angle, health, kills, deaths, is_alive, respawn_timer}
bullets = []  # list of dicts: {x, y, vx, vy, lifetime, owner_id}
match_winner = ""

# Pre-load Pygame walls server-side to calculate authoritative collisions
walls = [pygame.Rect(w[0], w[1], w[2], w[3]) for w in WALL_LAYOUTS]

def update_server_game_logic(dt):
    """Authoritative server loop tracking physics, collisions, and scores."""
    global match_winner
    if match_winner:
        return

    # 1. Update Bullet Lifetimes and Movement Mechanics
    for b in bullets[:]:
        b["x"] += b["vx"] * dt
        b["y"] += b["vy"] * dt
        b["lifetime"] -= dt

        b_rect = pygame.Rect(int(b["x"] - BULLET_SIZE//2), int(b["y"] - BULLET_SIZE//2), BULLET_SIZE, BULLET_SIZE)

        # Wall Obstacle Collision Checks
        hit_wall = False
        for wall in walls:
            if b_rect.colliderect(wall):
                if b in bullets: bullets.remove(b)
                hit_wall = True
                break
        if hit_wall or b["lifetime"] <= 0:
            if b in bullets and b["lifetime"] <= 0: bullets.remove(b)
            continue

        # Player Hit Detection Checks
        for p_id, p_data in players.items():
            if int(p_id) == b["owner_id"] or not p_data["is_alive"]:
                continue

            p_rect = pygame.Rect(int(p_data["x"] - PLAYER_SIZE//2), int(p_data["y"] - PLAYER_SIZE//2), PLAYER_SIZE, PLAYER_SIZE)
            if b_rect.colliderect(p_rect):
                # Apply authoritative server damage
                p_data["health"] -= BULLET_DAMAGE
                if b in bullets: bullets.remove(b)

                # Process elimination states
                if p_data["health"] <= 0:
                    p_data["health"] = 0
                    p_data["is_alive"] = False
                    p_data["respawn_timer"] = 3.0
                    p_data["deaths"] += 1
                    
                    # Award credit to shooter
                    if b["owner_id"] in players:
                        players[b["owner_id"]]["kills"] += 1
                        if players[b["owner_id"]]["kills"] >= 10:
                            match_winner = f"Player {b['owner_id']}"
                break

    # 2. Update Respawn Delays
    for p_id, p_data in players.items():
        if not p_data["is_alive"]:
            p_data["respawn_timer"] -= dt
            if p_data["respawn_timer"] <= 0.0:
                s_idx = int(p_id) % len(SPAWN_POINTS)
                p_data["x"], p_data["y"] = SPAWN_POINTS[s_idx]
                p_data["health"] = MAX_HEALTH
                p_data["is_alive"] = True

def server_ticks_loop():
    """Maintains a steady engine tick rate for the server updates."""
    last_time = time.time()
    while True:
        now = time.time()
        dt = now - last_time
        last_time = now
        update_server_game_logic(dt)
        time.sleep(1 / 60.0)

# Start global logic sync worker loop
threading.Thread(target=server_ticks_loop, daemon=True).start()

def handle_client(conn, player_id):
    global match_winner
    print(f"[SERVER] Connected to player slot: {player_id}")
    
    # Initialize authoritative state profile
    s_idx = player_id % len(SPAWN_POINTS)
    sx, sy = SPAWN_POINTS[s_idx]
    players[player_id] = {
        "x": sx, "y": sy, "angle": 0.0, "health": MAX_HEALTH,
        "kills": 0, "deaths": 0, "is_alive": True, "respawn_timer": 0.0
    }

    try:
        conn.send(str(player_id).encode())
    except socket.error:
        conn.close()
        return

    while True:
        try:
            data = conn.recv(4096)
            if not data:
                break
                
            client_payload = pickle.loads(data)
            
            # If match is active, read and store position inputs sent by the client
            if not match_winner and players[player_id]["is_alive"]:
                players[player_id]["x"] = client_payload.get("x", players[player_id]["x"])
                players[player_id]["y"] = client_payload.get("y", players[player_id]["y"])
                players[player_id]["angle"] = client_payload.get("angle", players[player_id]["angle"])

            # Check if the client requested to fire a shot
            if client_payload.get("shoot") and players[player_id]["is_alive"] and not match_winner:
                bx = client_payload["bx"]
                by = client_payload["by"]
                v_dx = client_payload["vx"]
                v_dy = client_payload["vy"]
                
                # Normalize firing vectors cleanly on the server side
                vec = pygame.Vector2(v_dx, v_dy)
                if vec.length_squared() > 0:
                    vec = vec.normalize() * BULLET_SPEED
                    bullets.append({
                        "x": bx, "y": by, "vx": vec.x, "vy": vec.y,
                        "lifetime": BULLET_LIFETIME, "owner_id": player_id
                    })

            # Package outbound response dictionary
            response_package = {
                "players": players,
                "bullets": [[b["x"], b["y"]] for b in bullets],
                "winner": match_winner
            }
            conn.sendall(pickle.dumps(response_package))
            
        except Exception:
            break

    print(f"[SERVER] Player disconnected slot: {player_id}")
    if player_id in players: del players[player_id]
    conn.close()

current_id = 0
while True:
    conn, addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, current_id), daemon=True).start()
    current_id += 1

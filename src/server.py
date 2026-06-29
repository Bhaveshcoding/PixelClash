import socket
import threading
import pickle
import time
import pygame
import random
import math
from constants import (
    SPAWN_POINTS, MAX_HEALTH, WALL_LAYOUTS, PLAYER_SIZE, BULLET_SIZE, 
    CRATE_LAYOUTS, CRATE_SIZE, WEAPON_PROFILES
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
print("[SERVER] Authoritative Server online. Physics layout successfully initiated.")

players = {}       
bullets = []       
grenades = []      
pickups = {}       
crates = []        
kill_feed = []     
match_winner = ""

# ❌ Critical Bug #2 Fixed: Cleanly unpack tuple layout indices via asterisk expansions
walls = [pygame.Rect(*w) for w in WALL_LAYOUTS]

def initialize_crates():
    """Generates 8 destructible storage crates using coordinate index indices unpacking."""
    global crates
    crates.clear()
    for idx, loc in enumerate(CRATE_LAYOUTS):
        # ❌ Critical Bug #3 Fixed: Extract x and y coordinates explicitly from map location tuples
        crates.append({
            "x": int(loc[0]), "y": int(loc[1]), "hp": 50, "id": idx
        })

initialize_crates()

pickup_spawn_timer = 15.0
pickup_id_counter = 0

def handle_pickup_spawning(dt):
    global pickup_spawn_timer, pickup_id_counter
    if len(pickups) >= 3:
        return
    pickup_spawn_timer -= dt
    if pickup_spawn_timer <= 0.0:
        pickup_spawn_timer = random.uniform(15.0, 20.0)
        chosen_type = random.choice(["HEALTH", "SPEED", "SHIELD", "DAMAGE"])
        px = random.randint(100, 1180)
        py = random.randint(100, 620)
        pickups[pickup_id_counter] = {"x": px, "y": py, "type": chosen_type}
        pickup_id_counter += 1

def update_server_game_logic(dt):
    global match_winner, kill_feed
    if match_winner: return

    handle_pickup_spawning(dt)

    for p_id, p in players.items():
        if not p["is_alive"]:
            p["respawn_timer"] -= dt
            if p["respawn_timer"] <= 0.0:
                s_idx = int(p_id) % len(SPAWN_POINTS)
                p["x"], p["y"] = SPAWN_POINTS[s_idx]
                p["health"] = MAX_HEALTH
                p["is_alive"] = True
                p["active_buff"] = "NONE"
                p["ammo"] = WEAPON_PROFILES[p["weapon_idx"]]["max_ammo"]
                kill_feed.append(f"Player {p_id} respawned")
                if len(kill_feed) > 5: kill_feed.pop(0)
            continue

        if p["reload_timer"] > 0.0:
            p["reload_timer"] -= dt
            if p["reload_timer"] <= 0.0:
                p["ammo"] = WEAPON_PROFILES[p["weapon_idx"]]["max_ammo"]

        if p["active_buff"] != "NONE":
            p["buff_timer"] -= dt
            if p["buff_timer"] <= 0.0: p["active_buff"] = "NONE"

        p_rect = pygame.Rect(int(p["x"] - PLAYER_SIZE//2), int(p["y"] - PLAYER_SIZE//2), PLAYER_SIZE, PLAYER_SIZE)
        for p_key in list(pickups.keys()):
            item = pickups[p_key]
            i_rect = pygame.Rect(item["x"] - 15, item["y"] - 15, 30, 30)
            if p_rect.colliderect(i_rect):
                if item["type"] == "HEALTH": p["health"] = min(MAX_HEALTH, p["health"] + 40)
                else:
                    p["active_buff"] = item["type"]
                    p["buff_timer"] = 8.0 if item["type"] == "DAMAGE" else 10.0
                del pickups[p_key]
                break

    for b in bullets[:]:
        b["x"] += b["vx"] * dt
        b["y"] += b["vy"] * dt
        b["lifetime"] -= dt
        b_rect = pygame.Rect(int(b["x"] - BULLET_SIZE//2), int(b["y"] - BULLET_SIZE//2), BULLET_SIZE, BULLET_SIZE)

        hit_something = False
        for crate in crates[:]:
            c_rect = pygame.Rect(crate["x"], crate["y"], CRATE_SIZE, CRATE_SIZE)
            if b_rect.colliderect(c_rect):
                crate["hp"] -= b["damage"]
                if b in bullets: bullets.remove(b)
                hit_something = True
                if crate["hp"] <= 0:
                    if random.random() < 0.4:
                        global pickup_id_counter
                        pickups[pickup_id_counter] = {
                            "x": crate["x"] + CRATE_SIZE//2, "y": crate["y"] + CRATE_SIZE//2,
                            "type": random.choice(["HEALTH", "SPEED", "SHIELD", "DAMAGE"])
                        }
                        pickup_id_counter += 1
                    crates.remove(crate)
                break
        if hit_something: continue

        for wall in walls:
            if b_rect.colliderect(wall):
                if b in bullets: bullets.remove(b)
                hit_something = True
                break
        if hit_something or b["lifetime"] <= 0:
            if b in bullets and b["lifetime"] <= 0: bullets.remove(b)
            continue

        for p_id, p in players.items():
            if int(p_id) == b["owner_id"] or not p["is_alive"]: continue
            p_rect = pygame.Rect(int(p["x"] - PLAYER_SIZE//2), int(p["y"] - PLAYER_SIZE//2), PLAYER_SIZE, PLAYER_SIZE)
            if b_rect.colliderect(p_rect):
                f_dmg = b["damage"]
                if p["active_buff"] == "SHIELD": f_dmg = int(f_dmg * 0.5)
                p["health"] -= f_dmg
                if b in bullets: bullets.remove(b)

                if p["health"] <= 0:
                    p["health"] = 0
                    p["is_alive"] = False
                    p["respawn_timer"] = 3.0
                    p["deaths"] += 1
                    if b["owner_id"] in players:
                        players[b["owner_id"]]["kills"] += 1
                        kill_feed.append(f"Player {b['owner_id']} killed Player {p_id}")
                        if len(kill_feed) > 5: kill_feed.pop(0)
                        if players[b["owner_id"]]["kills"] >= 10: match_winner = f"Player {b['owner_id']}"
                break

    for g in grenades[:]:
        g["x"] += g["vx"] * dt
        g["y"] += g["vy"] * dt
        g["vx"] *= 0.95
        g["vy"] *= 0.95
        g["timer"] -= dt

        g_rect = pygame.Rect(int(g["x"] - 8), int(g["y"] - 8), 16, 16)
        for wall in walls:
            if g_rect.colliderect(wall):
                g["vx"] = 0.0
                g["vy"] = 0.0
                break

        if g["timer"] <= 0.0:
            g_pos = pygame.Vector2(g["x"], g["y"])
            for p_id, p in players.items():
                if not p["is_alive"]: continue
                p_pos = pygame.Vector2(p["x"], p["y"])
                dist = g_pos.distance_to(p_pos)
                if dist <= 150:
                    g_dmg = int(60 * (1.0 - (dist / 150)))
                    if p["active_buff"] == "SHIELD": g_dmg = int(g_dmg * 0.5)
                    p["health"] -= g_dmg
                    if p["health"] <= 0:
                        p["health"] = 0
                        p["is_alive"] = False
                        p["respawn_timer"] = 3.0
                        p["deaths"] += 1
                        if g["owner_id"] in players:
                            players[g["owner_id"]]["kills"] += 1
                            kill_feed.append(f"Player {g['owner_id']} exploded Player {p_id}")
                            if len(kill_feed) > 5: kill_feed.pop(0)
                            if players[g["owner_id"]]["kills"] >= 10: match_winner = f"Player {g['owner_id']}"

            for crate in crates[:]:
                c_pos = pygame.Vector2(crate["x"] + CRATE_SIZE//2, crate["y"] + CRATE_SIZE//2)
                if g_pos.distance_to(c_pos) <= 150:
                    crate["hp"] -= 40
                    if crate["hp"] <= 0: crates.remove(crate)
            if g in grenades: grenades.remove(g)

def server_ticks_loop():
    last_time = time.time()
    while True:
        now = time.time()
        dt = now - last_time
        last_time = now
        update_server_game_logic(dt)
        time.sleep(1 / 60.0)

threading.Thread(target=server_ticks_loop, daemon=True).start()
def handle_client(conn, player_id):
    global match_winner, kill_feed
    print(f"[SERVER] Client connected slot index token assigned: {player_id}")
    
    s_idx = player_id % len(SPAWN_POINTS)
    sx, sy = SPAWN_POINTS[s_idx]
    
    players[player_id] = {
        "x": sx, "y": sy, "angle": 0.0, "health": MAX_HEALTH,
        "kills": 0, "deaths": 0, "is_alive": True, "respawn_timer": 0.0,
        "weapon_idx": 1, "ammo": 12, "reload_timer": 0.0,
        "active_buff": "NONE", "buff_timer": 0.0
    }

    try:
        conn.send(str(player_id).encode())
    except socket.error:
        conn.close()
        return

    while True:
        try:
            data = conn.recv(4096)
            if not data: break
            client_payload = pickle.loads(data)
            p = players[player_id]

            if client_payload.get("reset_match") and match_winner:
                match_winner = ""
                kill_feed.clear()
                initialize_crates()
                for pid, pl in players.items():
                    pl["kills"], pl["deaths"], pl["health"], pl["is_alive"] = 0, 0, MAX_HEALTH, True
                    pl["active_buff"] = "NONE"
                    st_idx = int(pid) % len(SPAWN_POINTS)
                    pl["x"], pl["y"] = SPAWN_POINTS[st_idx]

            if not match_winner and p["is_alive"]:
                p["x"] = client_payload.get("x", p["x"])
                p["y"] = client_payload.get("y", p["y"])
                p["angle"] = client_payload.get("angle", p["angle"])
                p["weapon_idx"] = client_payload.get("weapon_idx", p["weapon_idx"])
                
                if client_payload.get("request_reload") and p["reload_timer"] <= 0.0:
                    p["reload_timer"] = WEAPON_PROFILES[p["weapon_idx"]]["reload_time"]

            if client_payload.get("shoot") and p["is_alive"] and not match_winner and p["reload_timer"] <= 0.0:
                if p["ammo"] > 0:
                    w_idx = p["weapon_idx"]
                    w = WEAPON_PROFILES[w_idx]
                    
                    v_dx = client_payload["vx"]
                    v_dy = client_payload["vy"]
                    shoot_vec = pygame.Vector2(v_dx, v_dy)

                    if shoot_vec.length_squared() > 0:
                        p["ammo"] -= 1
                        dmg = w["damage"]
                        if p["active_buff"] == "DAMAGE": dmg *= 2
                        bx, by = client_payload["bx"], client_payload["by"]

                        if w_idx == 3: 
                            base_vec = shoot_vec.normalize()
                            base_ang = math.atan2(base_vec.y, base_vec.x)
                            for _ in range(5):
                                spread = random.uniform(-math.radians(w["spread"]), math.radians(w["spread"]))
                                final_ang = base_ang + spread
                                bullets.append({
                                    "x": bx, "y": by,
                                    "vx": math.cos(final_ang) * w["bullet_speed"], "vy": math.sin(final_ang) * w["bullet_speed"],
                                    "lifetime": 0.6, "owner_id": player_id, "damage": dmg
                                })
                        else: 
                            vec = shoot_vec.normalize()
                            bullets.append({
                                "x": bx, "y": by, "vx": vec.x * w["bullet_speed"], "vy": vec.y * w["bullet_speed"],
                                "lifetime": 1.5, "owner_id": player_id, "damage": dmg
                            })

            if client_payload.get("throw_grenade") and p["is_alive"] and not match_winner:
                gx, gy = p["x"], p["y"]
                g_vec = pygame.Vector2(client_payload["g_vx"], client_payload["g_vy"])
                if g_vec.length_squared() > 0:
                    g_vec = g_vec.normalize() * 550
                    grenades.append({
                        "x": gx, "y": gy, "vx": g_vec.x, "vy": g_vec.y,
                        "timer": 2.0, "owner_id": player_id
                    })

            response_package = {
                "players": players,
                "bullets": [[b["x"], b["y"]] for b in bullets],
                "grenades": [[g["x"], g["y"]] for g in grenades],
                "pickups": pickups,
                "crates": crates,
                "kill_feed": kill_feed,
                "winner": match_winner
            }
            conn.sendall(pickle.dumps(response_package))
        except Exception:
            break

    if player_id in players: del players[player_id]
    conn.close()

current_id = 0
while True:
    conn, addr = server_socket.accept()
    threading.Thread(target=handle_client, args=(conn, current_id), daemon=True).start()
    current_id += 1

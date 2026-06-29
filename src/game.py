import sys
import pygame
import random
import math
from replay import ReplayManager
from assets import assets
from camera import Camera
from constants import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, WALL_LAYOUTS,
    CROSSHAIR_COLOR, UI_COLOR, PLAYER_SIZE, BULLET_SIZE, CRATE_COLOR,
    GRENADE_COLOR, PICKUP_COLORS, CRATE_SIZE, WEAPON_PROFILES, EXPLOSION_COLOR
)
from player import Player
from wall import Wall
from network import Network
from menu import MenuSystem

class Game:
    def __init__(self):
        self.replay = ReplayManager()
        pygame.init()
        try:
            pygame.mixer.init()
            self.audio_available = True
        except pygame.error:
            print("[AUDIO WARN] No audio devices available. Sound features disabled.")
            self.audio_available = False
            
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        self.state_string = "MAIN_MENU"
        self.menu_manager = MenuSystem(self.screen)
        
        self.ui_font = assets.get_font(18, "Arial", True)
        self.hud_font = assets.get_font(28, "Impact")
        self.win_font = assets.get_font(72, "Impact")
        
        self.walls = [Wall(*w) for w in WALL_LAYOUTS]
        self.network = None
        self.player = None
        
        self.my_surf = assets.get_image("player_blue")
        self.enemy_surf = assets.get_image("player_red")

        self.camera = Camera()
        self.local_shoot_timer = 0.0
        self.hit_marker_timer = 0.0 
        self.particles = []

        self.server_players = {}
        self.server_bullets = []
        self.server_grenades = []
        self.server_pickups = {}
        self.server_crates = []
        self.server_kill_feed = []
        self.winner = ""

    def play_sound(self, action):

        if not self.audio_available:
            return

        if action == "shoot":

            shoot = assets.get_sound("shoot")

            if shoot:
                shoot.set_volume(self.menu_manager.sfx_volume)
                shoot.play()
    def spawn_particles(self, x, y, color, count=8, p_type="spark", size_range=(2, 5), life_range=(0.2, 0.5)):
        for _ in range(count):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(50, 250) if p_type != "smoke" else random.uniform(10, 40)
            
            min_l, max_l = life_range[0], life_range[1]
            max_life = random.uniform(min_l, max_l)
            
            min_s, max_s = size_range[0], size_range[1]
            size = random.randint(min_s, max_s)
            
            self.particles.append({
                "x": float(x), "y": float(y),
                "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed,
                "color": color, "life": max_life, "max_life": max_life,
                "size": size, "type": p_type
            })

    def establish_connection(self, ip):
        self.network = Network(ip)
        if self.network.p_id == -1:
            self.state_string = "MAIN_MENU"
            return
        self.player = Player(spawn_index=self.network.p_id % 4)
        pygame.mouse.set_visible(False)
        self.state_string = "GAMEPLAY"

    def handle_events(self):
    
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            if self.state_string == "JOIN_SCREEN":
                self.menu_manager.handle_keyboard_input(event)
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    if self.state_string == "GAMEPLAY":
                        self.state_string = "PAUSED"

                    elif self.state_string == "PAUSED":
                        self.state_string = "GAMEPLAY"

                elif event.key == pygame.K_F9:

                    self.replay.start()
            

    def update(self, dt: float):
        if self.state_string == "MAIN_MENU":
            cmd = self.menu_manager.draw_main_menu()
            if cmd == "HOST": self.establish_connection("127.0.0.1")
            elif cmd == "JOIN_SCREEN": self.state_string = "JOIN_SCREEN"
            elif cmd == "SETTINGS": self.state_string = "SETTINGS"
            elif cmd == "QUIT": self.is_running = False
            return

        if self.state_string == "JOIN_SCREEN":
            cmd, ip = self.menu_manager.draw_join_screen()
            if cmd == "CONNECT_ACTION": self.establish_connection(ip)
            elif cmd == "MAIN_MENU": self.state_string = "MAIN_MENU"
            return

        if self.state_string == "SETTINGS":
            cmd = self.menu_manager.draw_settings_screen()
            if cmd == "MAIN_MENU": self.state_string = "MAIN_MENU"
            elif cmd == "TOGGLE_FULLSCREEN":
                if self.menu_manager.is_fullscreen:
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                else:
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
                self.menu_manager.screen = self.screen
            return

        if self.state_string != "GAMEPLAY": return
        
        if self.replay.playing:

            frame = self.replay.next_frame()

            if frame is None:
                return

            self.server_players = frame["players"]
            self.server_bullets = frame["bullets"]
            self.server_grenades = frame["grenades"]
            self.server_pickups = frame["pickups"]
            self.server_crates = frame["crates"]
            self.server_kill_feed = frame["kill_feed"]
            self.winner = frame["winner"]

            return

        if self.local_shoot_timer > 0.0: self.local_shoot_timer -= dt
        if self.hit_marker_timer > 0.0: self.hit_marker_timer -= dt

        for p in self.particles[:]:
            p["life"] -= dt
            if p["type"] == "smoke": p["vy"] -= dt * 15.0  
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            if p["life"] <= 0: self.particles.remove(p)

        if not self.network or self.network.p_id == -1:
            self.state_string = "MAIN_MENU"
            pygame.mouse.set_visible(True)
            return

        me_s = self.server_players.get(self.network.p_id, {"active_buff": "none", "health": 100, "kills": 0})
        old_kills = me_s.get("kills", 0)

        self.player.handle_input(me_s.get("active_buff", "none"))
        self.player.update(dt, self.walls)
        self.camera.update(
            dt,
            self.player.pos
        )

        packet = {
            "x": self.player.pos.x, "y": self.player.pos.y, "angle": self.player.angle,
            "weapon_idx": self.player.weapon_idx, "request_reload": self.player.request_reload,
            "throw_grenade": self.player.request_grenade, "g_vx": self.player.grenade_target_vec.x,
            "g_vy": self.player.grenade_target_vec.y, "shoot": False
        }

        if pygame.mouse.get_pressed()[0] and self.local_shoot_timer <= 0.0 and me_s.get("is_alive", True) and not self.winner:
            if me_s.get("ammo", 1) > 0 and me_s.get("reload_timer", 0.0) <= 0.0:
                wp = WEAPON_PROFILES[self.player.weapon_idx]
                self.local_shoot_timer = wp["fire_rate"]
                packet["shoot"] = True
                packet["bx"], packet["by"] = self.player.pos.x, self.player.pos.y
                m_x, m_y = pygame.mouse.get_pos()
                packet["vx"], packet["vy"] = m_x - self.player.pos.x, m_y - self.player.pos.y
                
                rad = math.radians(self.player.angle)
                fx = self.player.pos.x + math.cos(rad) * 25
                fy = self.player.pos.y + math.sin(rad) * 25
                self.spawn_particles(fx, fy, (255, 230, 100), count=4, p_type="spark", size_range=(2, 4), life_range=(0.1, 0.3))
                self.spawn_particles(fx, fy, (160, 160, 160), count=2, p_type="smoke", life_range=(0.4, 0.8))
                self.camera.shake(0.1,4)
                self.camera.kick(-5,0)
                self.play_sound("shoot")

        if self.player.request_grenade and me_s.get("is_alive", True):
            self.camera.kick(-5, 0)
            self.camera.shake(0.12, 5)

        if self.winner and pygame.key.get_pressed()[pygame.K_SPACE]:
            packet["reset_match"] = True

        reply = self.network.send_and_receive(packet)
        
        if not reply:
            self.state_string = "MAIN_MENU"
            pygame.mouse.set_visible(True)
            return

        old_feed = self.server_kill_feed
        old_bullets_count = len(self.server_bullets)
        old_crates_count = len(self.server_crates)
        
        self.server_players = reply.get("players", {})
        self.server_bullets = reply.get("bullets", [])
        self.server_grenades = reply.get("grenades", [])
        self.server_pickups = reply.get("pickups", {})
        self.server_crates = reply.get("crates", {})
        self.server_kill_feed = reply.get("kill_feed", [])
        self.winner = reply.get("winner", "")
        
        new_me = self.server_players.get(self.network.p_id, {"kills": 0, "health": 100})
        if new_me.get("kills", 0) > old_kills or len(self.server_bullets) < old_bullets_count:
            self.hit_marker_timer = 0.15 

        if len(self.server_bullets) < old_bullets_count:
            for _ in range(old_bullets_count - len(self.server_bullets)):
                self.spawn_particles(self.player.pos.x + random.randint(-50, 50), self.player.pos.y + random.randint(-50, 50), (230, 230, 200), count=5, size_range=(1, 3), life_range=(0.2, 0.4))

        if len(self.server_crates) < old_crates_count:
            self.camera.shake(0.2, 8)
            self.spawn_particles(self.player.pos.x, self.player.pos.y, CRATE_COLOR, count=20, size_range=(3, 5), life_range=(0.3, 0.6))

        if len(self.server_kill_feed) > len(old_feed):
            self.camera.shake(0.3, 14)
            self.spawn_particles(self.player.pos.x, self.player.pos.y, EXPLOSION_COLOR, count=25, size_range=(4, 7), life_range=(0.4, 0.8))

        if self.network.p_id in self.server_players and not self.server_players[self.network.p_id]["is_alive"]:
            self.player.pos.x = self.server_players[self.network.p_id]["x"]
            self.player.pos.y = self.server_players[self.network.p_id]["y"]
        self.replay.record(
            self.server_players,
            self.server_bullets,
            self.server_grenades,
            self.server_pickups,
            self.server_crates,
            self.server_kill_feed,
            self.winner
        )
    def draw_world_entities(self, surface):
        for item in self.server_pickups.values():
            col = PICKUP_COLORS.get(item["type"], (255, 255, 255))
            float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 5 
            px, py = item["x"], item["y"] + float_offset
            pygame.draw.circle(surface, col, (int(px), int(py)), 16, 2)
            pygame.draw.rect(surface, col, (px - 8, py - 8, 16, 16), border_radius=3)

        for c in self.server_crates:
            pygame.draw.rect(surface, CRATE_COLOR, (c["x"], c["y"], CRATE_SIZE, CRATE_SIZE), border_radius=4)
            pygame.draw.rect(surface, (50, 20, 5), (c["x"], c["y"], CRATE_SIZE, CRATE_SIZE), 2, border_radius=4)

        for b in self.server_bullets:
            pygame.draw.rect(surface, (255, 215, 0), (int(b[0] - BULLET_SIZE//2), int(b[1] - BULLET_SIZE//2), BULLET_SIZE, BULLET_SIZE))

        for g in self.server_grenades:
            pygame.draw.circle(surface, GRENADE_COLOR, (int(g[0]), int(g[1])), 8)

        for p in self.particles:
            alpha = int(255 * (p["life"] / p["max_life"]))
            p_surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
            r, g, b = p["color"][0], p["color"][1], p["color"][2]
            pygame.draw.circle(p_surf, (r, g, b, alpha), (p["size"], p["size"]), p["size"])
            surface.blit(p_surf, (int(p["x"] - p["size"]), int(p["y"] - p["size"])))

        for pid, p in self.server_players.items():
            if not p["is_alive"]: continue
            base = self.my_surf if int(pid) == self.network.p_id else self.enemy_surf
            rot = pygame.transform.rotate(base, -p["angle"])
            r_rect = rot.get_rect(center=(int(p["x"]), int(p["y"])))
            surface.blit(rot, r_rect)

            bx, by = r_rect.centerx - 30, r_rect.top - 14
            pygame.draw.rect(surface, (15, 15, 20), (bx, by, 60, 6), border_radius=2)
            pw = int(58 * (p["health"] / 100))
            if pw > 0: pygame.draw.rect(surface, (40, 220, 100), (bx + 1, by + 1, pw, 4), border_radius=1)

            lbl_col = (0, 220, 255) if int(pid) == self.network.p_id else (255, 100, 100)
            name_txt = self.ui_font.render(f"P{pid}", True, lbl_col)
            surface.blit(name_txt, (r_rect.centerx - name_txt.get_width()//2, by - 18))

    def draw_hud_overlays(self):
        kf_y = 30
        for entry in self.server_kill_feed:
            txt = self.ui_font.render(f"NOTICE » {entry}", True, (255, 80, 80))
            bg_bar = pygame.Surface((txt.get_width() + 16, 24), pygame.SRCALPHA)
            bg_bar.fill((0, 0, 0, 100))
            self.screen.blit(bg_bar, (15, kf_y - 2))
            self.screen.blit(txt, (23, kf_y))
            kf_y += 28

        score_y = 30
        panel_w = 220
        pygame.draw.rect(self.screen, (20, 20, 25, 180), (WIDTH - panel_w - 20, score_y, panel_w, 35 + (len(self.server_players) * 26)), border_radius=6)
        hdr = self.ui_font.render("ARENA LEADERBOARD", True, (150, 160, 180))
        self.screen.blit(hdr, (WIDTH - panel_w, score_y + 8))
        
        sorted_players = sorted(self.server_players.items(), key=lambda x: x[1]["kills"], reverse=True)
        item_y = score_y + 30
        for pid, pl in sorted_players:
            lbl = "YOU" if int(pid) == self.network.p_id else f"PLAYER {pid}"
            lbl_col = (0, 200, 255) if int(pid) == self.network.p_id else UI_COLOR
            stxt = self.ui_font.render(f"{lbl.ljust(10)} {pl['kills']} K / {pl['deaths']} D", True, lbl_col)
            self.screen.blit(stxt, (WIDTH - panel_w, item_y))
            item_y += 24

        me = self.server_players.get(self.network.p_id, {})
        if me:
            wp = WEAPON_PROFILES[me.get("weapon_idx", 1)]
            ammo = me.get("ammo", 0)
            r_time = me.get("reload_timer", 0.0)
            
            w_txt = self.hud_font.render(wp["name"].upper(), True, (255, 255, 255))
            self.screen.blit(w_txt, (35, HEIGHT - 85))
            
            ammo_str = f"AMMO: {ammo} / {wp['max_ammo']}" if r_time <= 0.0 else "STATE: RELOADING..."
            ammo_col = (255, 215, 0) if ammo > 0 else (255, 50, 50)
            a_txt = self.hud_font.render(ammo_str, True, ammo_col)
            self.screen.blit(a_txt, (35, HEIGHT - 55))

        if self.menu_manager.show_fps:
            fps_str = f"FPS: {int(self.clock.get_fps())}"
            fps_txt = self.ui_font.render(fps_str, True, (0, 255, 150))
            self.screen.blit(fps_txt, (20, HEIGHT - 30))

        m_pos = pygame.mouse.get_pos()
        if self.hit_marker_timer > 0.0:
            pygame.draw.line(self.screen, (255, 50, 50), (m_pos[0] - 8, m_pos[1] - 8), (m_pos[0] - 3, m_pos[1] - 3), 2)
            pygame.draw.line(self.screen, (255, 50, 50), (m_pos[0] + 3, m_pos[1] + 3), (m_pos[0] + 8, m_pos[1] + 8), 2)
            pygame.draw.line(self.screen, (255, 50, 50), (m_pos[0] + 3, m_pos[1] - 3), (m_pos[0] + 8, m_pos[1] - 8), 2)
            pygame.draw.line(self.screen, (255, 50, 50), (m_pos[0] - 8, m_pos[1] + 3), (m_pos[0] - 3, m_pos[1] + 8), 2)
        else:
            pygame.draw.circle(self.screen, CROSSHAIR_COLOR, m_pos, 6, 2)
            pygame.draw.circle(self.screen, CROSSHAIR_COLOR, m_pos, 2, 0)

        if self.winner:

            self.camera.set_zoom(1.2)
            
        else:

            self.camera.set_zoom(1.0)

    def draw(self):
        if self.state_string == "MAIN_MENU":
            cmd = self.menu_manager.draw_main_menu()
            if cmd == "HOST": self.establish_connection("127.0.0.1")
            elif cmd == "JOIN_SCREEN": self.state_string = "JOIN_SCREEN"
            elif cmd == "SETTINGS": self.state_string = "SETTINGS"
            elif cmd == "QUIT": self.is_running = False
            pygame.display.flip()
            return

        if self.state_string == "JOIN_SCREEN":
            cmd, ip = self.menu_manager.draw_join_screen()
            if cmd == "CONNECT_ACTION": self.establish_connection(ip)
            elif cmd == "MAIN_MENU": self.state_string = "MAIN_MENU"
            pygame.display.flip()
            return

        if self.state_string == "SETTINGS":
            cmd = self.menu_manager.draw_settings_screen()
            if cmd == "MAIN_MENU": self.state_string = "MAIN_MENU"
            elif cmd == "TOGGLE_FULLSCREEN":
                if self.menu_manager.is_fullscreen:
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
                else:
                    self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
                self.menu_manager.screen = self.screen
            pygame.display.flip()
            return
            
        canvas = pygame.Surface((WIDTH, HEIGHT))
        canvas.fill(BACKGROUND_COLOR)
        for wall in self.walls: wall.draw(canvas)
        self.draw_world_entities(canvas)
        offset = self.camera.get_offset()

        self.screen.fill(BACKGROUND_COLOR)

        self.screen.blit(
            canvas,
            (-offset.x, -offset.y)
        )
        self.draw_hud_overlays()
        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

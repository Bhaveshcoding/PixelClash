import sys
import pygame
from constants import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, 
    WALL_LAYOUTS, CROSSHAIR_COLOR, UI_COLOR, PLAYER_SIZE, BULLET_SIZE
)
from player import Player
from wall import Wall
from network import Network

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        pygame.mouse.set_visible(False)
        self.ui_font = pygame.font.SysFont(None, 32)
        self.win_font = pygame.font.SysFont(None, 64)

        self.walls = [Wall(w[0], w[1], w[2], w[3]) for w in WALL_LAYOUTS]
        self.network = Network()
        
        if self.network.p_id == -1:
            pygame.quit()
            sys.exit()

        self.player = Player(spawn_index=self.network.p_id % 4)
        
        # Local asset surface variations
        self.my_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self.my_surf.fill((0, 200, 255)) # Cyan for Local Player
        pygame.draw.rect(self.my_surf, (30, 30, 30), (PLAYER_SIZE - 10, (PLAYER_SIZE // 2) - 5, 10, 10))

        self.enemy_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self.enemy_surf.fill((255, 100, 100)) # Red for Network Enemies
        pygame.draw.rect(self.enemy_surf, (80, 20, 20), (PLAYER_SIZE - 10, (PLAYER_SIZE // 2) - 5, 10, 10))

        self.b_surf = pygame.Surface((BULLET_SIZE, BULLET_SIZE))
        self.b_surf.fill((255, 215, 0))

        # Dynamic structural containers updated by network payloads
        self.server_players = {}
        self.server_bullets = []
        self.winner = ""

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

    def update(self, dt: float):
        self.player.handle_input()
        self.player.update(dt, self.walls)

        # Package local positions into the data packet
        packet = {
            "x": self.player.pos.x,
            "y": self.player.pos.y,
            "angle": self.player.angle,
            "shoot": False
        }

        # Handle shooting input and track local weapon cooldowns
        mouse_click = pygame.mouse.get_pressed()[0]
        # Check if the player is alive according to the server before allowing them to shoot
        me_server = self.server_players.get(self.network.p_id, {"is_alive": True})
        
        if mouse_click and self.player.shoot_timer <= 0.0 and me_server.get("is_alive", True) and not self.winner:
            self.player.shoot_timer = 0.2 # Reset local fire cooldown
            m_x, m_y = pygame.mouse.get_pos()
            packet["shoot"] = True
            packet["bx"] = self.player.pos.x
            packet["by"] = self.player.pos.y
            packet["vx"] = m_x - self.player.pos.x
            packet["vy"] = m_y - self.player.pos.y

        # Sync with Authoritative Server data payload
        reply = self.network.send_and_receive(packet)
        if reply:
            self.server_players = reply.get("players", {})
            self.server_bullets = reply.get("bullets", [])
            self.winner = reply.get("winner", "")
            
            # Snap local coordinates to server state if killed to sync respawns cleanly
            if self.network.p_id in self.server_players:
                if not self.server_players[self.network.p_id]["is_alive"]:
                    self.player.pos.x = self.server_players[self.network.p_id]["x"]
                    self.player.pos.y = self.server_players[self.network.p_id]["y"]

    def draw_game_world(self):
        """Draws players, health bars, and bullets using server data."""
        # 1. Draw Bullets sent by server
        for b_pos in self.server_bullets:
            b_rect = self.b_surf.get_rect(center=(int(b_pos[0]), int(b_pos[1])))
            self.screen.blit(self.b_surf, b_rect)

        # 2. Draw Players and health bars sent by server
        for p_id, p in self.server_players.items():
            if not p["is_alive"]:
                continue
                
            # Use Cyan surface for local player, Red surface for opponents
            base = self.my_surf if int(p_id) == self.network.p_id else self.enemy_surf
            rot_surf = pygame.transform.rotate(base, -p["angle"])
            rot_rect = rot_surf.get_rect(center=(int(p["x"]), int(p["y"])))
            self.screen.blit(rot_surf, rot_rect)

            # Render Health Bar above players
            bx = rot_rect.centerx - 25
            by = rot_rect.top - 10
            pygame.draw.rect(self.screen, (200, 30, 30), (bx, by, 50, 5))
            pct_w = int(50 * (p["health"] / 100))
            pygame.draw.rect(self.screen, (30, 200, 30), (bx, by, pct_w, 5))

    def draw_ui_and_overlays(self):
        # Render top corner score statistics panel
        y_off = 20
        for p_id, p in self.server_players.items():
            lbl = "You" if int(p_id) == self.network.p_id else f"Player {p_id}"
            txt = self.ui_font.render(f"{lbl} - Kills: {p['kills']} Deaths: {p['deaths']}", True, UI_COLOR)
            self.screen.blit(txt, (20, y_off))
            y_off += 30

        # Render Full-Screen Victory Overlay
        if self.winner:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            self.screen.blit(overlay, (0, 0))
            w_txt = self.win_font.render(f"{self.winner.upper()} WINS MATCH!", True, (255, 215, 0))
            self.screen.blit(w_txt, (WIDTH//2 - w_txt.get_width()//2, HEIGHT//2 - 30))

        # Render Crosshair
        m_pos = pygame.mouse.get_pos()
        m_vec = pygame.Vector2(m_pos)
        pygame.draw.circle(self.screen, CROSSHAIR_COLOR, m_pos, 8, 2)
        pygame.draw.line(self.screen, CROSSHAIR_COLOR, (m_vec.x - 12, m_vec.y), (m_vec.x + 12, m_vec.y), 2)
        pygame.draw.line(self.screen, CROSSHAIR_COLOR, (m_vec.x, m_vec.y - 12), (m_vec.x, m_vec.y + 12), 2)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        for wall in self.walls:
            wall.draw(self.screen)
        self.draw_game_world()
        self.draw_ui_and_overlays()
        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()

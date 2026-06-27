import sys
import pygame
from constants import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, 
    WALL_LAYOUTS, CROSSHAIR_COLOR, DUMMY_COLOR, PLAYER_SIZE
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
        self.walls = []
        self.build_arena()

        # 1. Initialize Network Interface
        print("[LAUNCH] Connecting to multiplayer infrastructure...")
        self.network = Network()
        
        if self.network.p_id == -1:
            print("[CRITICAL] Could not reach server. Booting in fallback mode.")
            pygame.quit()
            sys.exit()

        # 2. Local Player Setup (Spawn point determined by unique Network ID assignment)
        spawn_idx = self.network.p_id % 4
        self.player = Player(spawn_index=spawn_idx, name=f"Player {self.network.p_id}")
        
        # Local mirror mapping of all foreign remote network players online
        self.remote_players_data = {}

        # Pre-compile a basic remote enemy display rectangle lookalike surface
        self.enemy_base_surf = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE), pygame.SRCALPHA)
        self.enemy_base_surf.fill(DUMMY_COLOR)
        pygame.draw.rect(self.enemy_base_surf, (80, 20, 20), (PLAYER_SIZE - 10, (PLAYER_SIZE // 2) - 5, 10, 10))

    def build_arena(self):
        for item in WALL_LAYOUTS:
            x, y, w, h = item
            self.walls.append(Wall(x, y, w, h))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

    def update(self, dt: float):
        # 1. Standard local input & positional sweeps
        self.player.handle_input()
        self.player.update(dt, self.walls)
        self.player.update_aim()

        # 2. Bundle local layout physics to package upstream
        local_payload = {
            "x": self.player.pos.x,
            "y": self.player.pos.y,
            "angle": self.player.angle
        }

        # 3. Transmit state payload to server and get back the update dictionary
        self.remote_players_data = self.network.send_and_receive(local_payload)

    def draw_network_players(self):
        """Iterates and draws other active network players on the map."""
        for p_id, data in self.remote_players_data.items():
            # Skip drawing yourself
            if int(p_id) == self.network.p_id:
                continue
                
            # Safely fetch orientation coordinates from data dictionary
            rx = data.get("x", 0.0)
            ry = data.get("y", 0.0)
            r_angle = data.get("angle", 0.0)

            # Generate rotated temporary render surface matching remote player direction
            rot_surf = pygame.transform.rotate(self.enemy_base_surf, -r_angle)
            rot_rect = rot_surf.get_rect(center=(int(rx), int(ry)))
            
            self.screen.blit(rot_surf, rot_rect)

    def draw_crosshair(self):
        m_pos = pygame.mouse.get_pos()
        m_vec = pygame.Vector2(m_pos)
        pygame.draw.circle(self.screen, CROSSHAIR_COLOR, m_pos, 8, 2)
        pygame.draw.line(self.screen, CROSSHAIR_COLOR, (m_vec.x - 12, m_vec.y), (m_vec.x + 12, m_vec.y), 2)
        pygame.draw.line(self.screen, CROSSHAIR_COLOR, (m_vec.x, m_vec.y - 12), (m_vec.x, m_vec.y + 12), 2)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        for wall in self.walls:
            wall.draw(self.screen)
            
        # Draw remote opponent entities sent from server
        self.draw_network_players()
            
        self.player.draw(self.screen)
        self.draw_crosshair()
        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()

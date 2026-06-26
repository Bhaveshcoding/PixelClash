import sys
import pygame
from constants import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, WALL_LAYOUTS
from player import Player
from wall import Wall

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # Core Game Entities
        self.player = Player()
        self.walls = []
        
        # Populate World Map Geometry once on initialization
        self.build_arena()

    def build_arena(self):
        """Translates layout coordinates into structural map entities."""
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
        self.player.handle_input()
        self.player.update(dt, self.walls)

    def draw(self):
        # 1. Render Background Canvas
        self.screen.fill(BACKGROUND_COLOR)
        
        # 2. Render Static World Environment
        for wall in self.walls:
            wall.draw(self.screen)
            
        # 3. Render Active Mobile Entities
        self.player.draw(self.screen)
        
        # 4. Present the full render layer stack
        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()

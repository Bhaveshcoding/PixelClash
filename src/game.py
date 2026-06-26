# src/game.py
import sys
import pygame
from constants import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR
from player import Player

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        self.player = Player()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

    def update(self, dt: float):
        # Call handle_input with no arguments
        self.player.handle_input()
        # Pass dt into update
        self.player.update(dt)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        self.player.draw(self.screen)
        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()

import pygame
from constants import WALL_COLOR

class Wall:
    def __init__(self, x: float, y: float, width: float, height: float):
        # Establish the physical boundary box
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        
        # Build the static graphic asset
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill(WALL_COLOR)

    def draw(self, surface: pygame.Surface):
        """Draws the obstacle block to the provided surface."""
        surface.blit(self.surface, self.rect)

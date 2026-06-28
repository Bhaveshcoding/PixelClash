import pygame
from constants import WALL_COLOR

class Wall:
    def __init__(self, x: float, y: float, width: float, height: float):
        self.rect = pygame.Rect(int(x), int(y), int(width), int(height))
        self.surface = pygame.Surface((self.rect.width, self.rect.height))
        self.surface.fill(WALL_COLOR)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.rect)

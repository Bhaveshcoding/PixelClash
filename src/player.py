# src/player.py
import pygame
from constants import (
    WIDTH, HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, 
    PLAYER_SPEED, PLAYER_COLOR
)

class Player:
    def __init__(self):
        self.pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = PLAYER_SPEED
        
        self.surface = pygame.Surface((self.width, self.height))
        self.surface.fill(PLAYER_COLOR)
        self.rect = self.surface.get_rect()

    def handle_input(self):
        """Reads keyboard state and generates a movement velocity vector."""
        keys = pygame.key.get_pressed()
        self.velocity = pygame.Vector2(0, 0)

        if keys[pygame.K_w]: self.velocity.y -= 1
        if keys[pygame.K_s]: self.velocity.y += 1
        if keys[pygame.K_a]: self.velocity.x -= 1
        if keys[pygame.K_d]: self.velocity.x += 1

        # Normalize diagonal travel vector
        if self.velocity.length_squared() > 0:
            self.velocity = self.velocity.normalize() * self.speed

    def update(self, dt: float):
        """Applies movement tracking with delta-time and clamps to boundaries."""
        self.pos += self.velocity * dt

        # Keep player fully inside screen borders
        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x > WIDTH - self.width:
            self.pos.x = WIDTH - self.width

        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y > HEIGHT - self.height:
            self.pos.y = HEIGHT - self.height

        # Sync visual rendering rectangle with position vector
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.rect)

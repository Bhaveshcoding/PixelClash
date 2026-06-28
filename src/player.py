import pygame
import math
from constants import PLAYER_SIZE, PLAYER_SPEED, PLAYER_COLOR, SPAWN_POINTS, FIRE_COOLDOWN

class Player:
    def __init__(self, spawn_index: int):
        start_x, start_y = SPAWN_POINTS[spawn_index]
        self.pos = pygame.Vector2(start_x, start_y)
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 0.0
        self.shoot_timer = 0.0
        
        self.base_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.base_surface.fill(PLAYER_COLOR)
        pygame.draw.rect(self.base_surface, (30, 30, 30), (self.size - 10, (self.size // 2) - 5, 10, 10))
        self.surface = self.base_surface.copy()
        self.rect = self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0

        if keys[pygame.K_w]: self.velocity.y -= 1
        if keys[pygame.K_s]: self.velocity.y += 1
        if keys[pygame.K_a]: self.velocity.x -= 1
        if keys[pygame.K_d]: self.velocity.x += 1

        if self.velocity.length_squared() > 0:
            self.velocity = self.velocity.normalize() * self.speed

    def update(self, dt: float, walls: list):
        """Calculates temporary local movements and checks them against wall boundaries."""
        if self.shoot_timer > 0.0:
            self.shoot_timer -= dt

        # Resolve horizontal axis collisions
        self.pos.x += self.velocity.x * dt
        self.rect.centerx = int(self.pos.x)
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity.x > 0: self.rect.right = wall.rect.left
                elif self.velocity.x < 0: self.rect.left = wall.rect.right
                self.pos.x = float(self.rect.centerx)

        # Resolve vertical axis collisions
        self.pos.y += self.velocity.y * dt
        self.rect.centery = int(self.pos.y)
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity.y > 0: self.rect.bottom = wall.rect.top
                elif self.velocity.y < 0: self.rect.top = wall.rect.bottom
                self.pos.y = float(self.rect.centery)

        # Update player aiming rotation angle based on mouse coordinates
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.pos.x
        dy = mouse_y - self.pos.y
        self.angle = math.degrees(math.atan2(dy, dx))

import pygame
from constants import BULLET_SIZE, BULLET_COLOR

class Bullet:
    def __init__(self, start_pos: pygame.Vector2, direction_vec: pygame.Vector2, speed: float, lifetime: float):
        self.pos = pygame.Vector2(start_pos.x, start_pos.y)
        self.velocity = direction_vec.normalize() * speed
        self.lifetime = lifetime
        self.size = BULLET_SIZE
        
        # Build the bullet visual block
        self.surface = pygame.Surface((self.size, self.size))
        self.surface.fill(BULLET_COLOR)
        self.rect = self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def update(self, dt: float):
        """Advances the position vector and counts down remaining lifetime."""
        self.pos += self.velocity * dt
        self.lifetime -= dt
        
        # Synchronize collision box tracking
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def is_dead(self) -> bool:
        """Returns True if the projectile has exceeded its lifetime."""
        return self.lifetime <= 0

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.rect)

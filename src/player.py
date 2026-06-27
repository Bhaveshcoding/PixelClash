import pygame
import math
from constants import PLAYER_SIZE, PLAYER_SPEED, PLAYER_COLOR, SPAWN_POINTS, FIRE_COOLDOWN, BULLET_SPEED, BULLET_LIFETIME
from bullet import Bullet

class Player:
    def __init__(self):
        start_x, start_y = SPAWN_POINTS[0]
        self.pos = pygame.Vector2(start_x, start_y)
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 0.0                  # Heading orientation in degrees
        self.shoot_timer = 0.0            # Tracks continuous fire rate padding
        
        # Core visual block and directional pointer indicator
        self.base_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.base_surface.fill(PLAYER_COLOR)
        # Paint a small dark pointing node on the front face edge
        pygame.draw.rect(self.base_surface, (0, 100, 150), (self.size - 10, (self.size // 2) - 5, 10, 10))
        
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

    def update_aim(self):
        """Calculates rotation angle towards the current mouse location."""
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate offset vector from the player's center position
        dx = mouse_x - self.pos.x
        dy = mouse_y - self.pos.y
        
        # Compute tracking arc and convert to degrees
        self.angle = math.degrees(math.atan2(dy, dx))
        
        # Rotate the graphic surface to match the new angle
        self.surface = pygame.transform.rotate(self.base_surface, -self.angle)
        self.rect = self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def can_shoot(self) -> bool:
        """Validates weapon firing state against the active cooldown clock."""
        return self.shoot_timer <= 0.0

    def shoot(self) -> Bullet:
        """Spawns a new bullet aimed directly at the mouse cursor."""
        self.shoot_timer = FIRE_COOLDOWN
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Create a direction vector pointing from the player towards the mouse
        dir_vec = pygame.Vector2(mouse_x - self.pos.x, mouse_y - self.pos.y)
        if dir_vec.length_squared() == 0:
            dir_vec = pygame.Vector2(1, 0) # Fallback vector if mouse is on player
            
        return Bullet(self.pos, dir_vec, BULLET_SPEED, BULLET_LIFETIME)

    def update(self, dt: float, walls: list):
        """Processes movement and updates the weapon cooldown timer."""
        if self.shoot_timer > 0.0:
            self.shoot_timer -= dt

        # Horizontal movement and collision pass
        self.pos.x += self.velocity.x * dt
        self.rect.centerx = int(self.pos.x)
        self.process_collisions(walls, axis='x')

        # Vertical movement and collision pass
        self.pos.y += self.velocity.y * dt
        self.rect.centery = int(self.pos.y)
        self.process_collisions(walls, axis='y')
        
        self.update_aim()

    def process_collisions(self, walls: list, axis: str):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if axis == 'x':
                    if self.velocity.x > 0:  self.rect.right = wall.rect.left
                    elif self.velocity.x < 0: self.rect.left = wall.rect.right
                    self.pos.x = float(self.rect.centerx)
                elif axis == 'y':
                    if self.velocity.y > 0:  self.rect.bottom = wall.rect.top
                    elif self.velocity.y < 0: self.rect.top = wall.rect.bottom
                    self.pos.y = float(self.rect.centery)

    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, self.rect)

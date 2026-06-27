import pygame
import math
import random
from constants import (
    PLAYER_SIZE, PLAYER_SPEED, PLAYER_COLOR, SPAWN_POINTS, 
    FIRE_COOLDOWN, BULLET_SPEED, BULLET_LIFETIME, MAX_HEALTH,
    DASH_SPEED_MULTIPLIER, DASH_DURATION, DASH_COOLDOWN
)
from bullet import Bullet

class Player:
    def __init__(self, spawn_index: int = 0, color: tuple = PLAYER_COLOR, name: str = "Player"):
        self.spawn_index = spawn_index
        self.color = color
        self.name = name
        
        # Identity Staging Status
        self.health = MAX_HEALTH
        self.max_health = MAX_HEALTH
        self.is_alive = True
        self.respawn_timer = 0.0
        self.kills = 0
        self.deaths = 0
        
        # Dash Attributes
        self.dash_timer = 0.0             # Tracks active burst execution duration
        self.dash_cooldown_timer = 0.0    # Tracks total cooldown recovery padding
        self.dash_direction = pygame.Vector2(0, 0)
        
        # Physics Coordinates
        self.reset_to_spawn()
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 0.0                  
        self.shoot_timer = 0.0            
        
        # Visual Asset Bases
        self.base_surface = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        self.base_surface.fill(self.color)
        pygame.draw.rect(self.base_surface, (30, 30, 30), (self.size - 10, (self.size // 2) - 5, 10, 10))
        
        self.surface = self.base_surface.copy()
        self.rect = self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def reset_to_spawn(self):
        """Teleports the entity to their designated starting point and resets health."""
        start_x, start_y = SPAWN_POINTS[self.spawn_index]
        self.pos = pygame.Vector2(start_x, start_y)
        self.health = self.max_health
        self.is_alive = True
        self.respawn_timer = 0.0
        self.dash_timer = 0.0

    def take_damage(self, amount: int) -> bool:
        """Applies damage and returns True if the hit eliminates the player."""
        if not self.is_alive:
            return False
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.is_alive = False
            self.deaths += 1
            self.respawn_timer = 3.0  # 3 Second Respawn Delay
            return True
        return False

    def handle_input(self):
        if not self.is_alive:
            return
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0

        if keys[pygame.K_w]: self.velocity.y -= 1
        if keys[pygame.K_s]: self.velocity.y += 1
        if keys[pygame.K_a]: self.velocity.x -= 1
        if keys[pygame.K_d]: self.velocity.x += 1

        if self.velocity.length_squared() > 0:
            self.velocity = self.velocity.normalize() * self.speed
            
            # Check for Dash Trigger Input (Left Shift)
            if keys[pygame.K_LSHIFT] and self.dash_cooldown_timer <= 0.0 and self.dash_timer <= 0.0:
                self.dash_timer = DASH_DURATION
                self.dash_cooldown_timer = DASH_COOLDOWN
                self.dash_direction = self.velocity.normalize()

    def update_aim(self, target_pos: tuple = None):
        if not self.is_alive:
            return
        # Use mouse target position by default, or an explicit position override (for AI/Dummies)
        aim_x, aim_y = target_pos if target_pos else pygame.mouse.get_pos()
        dx = aim_x - self.pos.x
        dy = aim_y - self.pos.y
        
        self.angle = math.degrees(math.atan2(dy, dx))
        self.surface = pygame.transform.rotate(self.base_surface, -self.angle)
        self.rect = self.surface.get_rect(center=(int(self.pos.x), int(self.pos.y)))

    def can_shoot(self) -> bool:
        return self.is_alive and self.shoot_timer <= 0.0

    def shoot(self, target_pos: tuple = None) -> Bullet:
        self.shoot_timer = FIRE_COOLDOWN
        aim_x, aim_y = target_pos if target_pos else pygame.mouse.get_pos()
        dir_vec = pygame.Vector2(aim_x - self.pos.x, aim_y - self.pos.y)
        if dir_vec.length_squared() == 0:
            dir_vec = pygame.Vector2(1, 0)
        return Bullet(self.pos, dir_vec, BULLET_SPEED, BULLET_LIFETIME, owner=self)

    def update(self, dt: float, walls: list):
        # Handle death and countdown the respawn timer
        if not self.is_alive:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0.0:
                self.reset_to_spawn()
            return

        # Cooldown timer count down passes
        if self.shoot_timer > 0.0:
            self.shoot_timer -= dt
        if self.dash_cooldown_timer > 0.0:
            self.dash_cooldown_timer -= dt

        # Calculate movement vector based on standard speed vs active dash burst modifiers
        current_move = self.velocity
        if self.dash_timer > 0.0:
            self.dash_timer -= dt
            current_move = self.dash_direction * (self.speed * DASH_SPEED_MULTIPLIER)

        # Separate axis update runs to calculate wall sliding accurately
        self.pos.x += current_move.x * dt
        self.rect.centerx = int(self.pos.x)
        self.process_collisions(walls, axis='x')

        self.pos.y += current_move.y * dt
        self.rect.centery = int(self.pos.y)
        self.process_collisions(walls, axis='y')

    def process_collisions(self, walls: list, axis: str):
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if axis == 'x':
                    if self.velocity.x > 0 or self.dash_direction.x > 0: self.rect.right = wall.rect.left
                    elif self.velocity.x < 0 or self.dash_direction.x < 0: self.rect.left = wall.rect.right
                    self.pos.x = float(self.rect.centerx)
                elif axis == 'y':
                    if self.velocity.y > 0 or self.dash_direction.y > 0: self.rect.bottom = wall.rect.top
                    elif self.velocity.y < 0 or self.dash_direction.y < 0: self.rect.top = wall.rect.bottom
                    self.pos.y = float(self.rect.centery)

    def draw_health_bar(self, surface: pygame.Surface):
        """Draws a multi-colored health bar centered directly above the entity block."""
        if not self.is_alive:
            return
        bar_width = 50
        bar_height = 6
        bar_x = self.rect.centerx - (bar_width // 2)
        bar_y = self.rect.top - 12
        
        # Calculate remaining health percentage width
        health_pct = self.health / self.max_health
        fill_width = int(bar_width * health_pct)
        
        # Layer Red base background with Green overlay fill
        pygame.draw.rect(surface, (200, 30, 30), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (30, 200, 30), (bar_x, bar_y, fill_width, bar_height))

    def draw(self, surface: pygame.Surface):
        if not self.is_alive:
            return
        surface.blit(self.surface, self.rect)
        self.draw_health_bar(surface)

import pygame
import math
from constants import PLAYER_SIZE, PLAYER_SPEED, SPAWN_POINTS

class Player:
    def __init__(self, spawn_index: int):
        start_x, start_y = SPAWN_POINTS[spawn_index]
        self.pos = pygame.Vector2(start_x, start_y)
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.velocity = pygame.Vector2(0, 0)
        self.angle = 0.0
        
        self.rect = pygame.Rect(int(self.pos.x - self.size//2), int(self.pos.y - self.size//2), self.size, self.size)
        
        self.weapon_idx = 1  # 1 = Pistol, 2 = SMG, 3 = Shotgun
        self.request_reload = False
        self.request_grenade = False
        self.grenade_target_vec = pygame.Vector2(0, 0)

    def handle_input(self, current_buff="none"):
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0
        self.request_reload = False
        self.request_grenade = False

        if keys[pygame.K_w]: self.velocity.y -= 1
        if keys[pygame.K_s]: self.velocity.y += 1
        if keys[pygame.K_a]: self.velocity.x -= 1
        if keys[pygame.K_d]: self.velocity.x += 1

        move_speed = self.speed
        if current_buff == "SPEED":
            move_speed *= 1.5

        if self.velocity.length_squared() > 0:
            self.velocity = self.velocity.normalize() * move_speed

        if keys[pygame.K_1]: self.weapon_idx = 1
        if keys[pygame.K_2]: self.weapon_idx = 2
        if keys[pygame.K_3]: self.weapon_idx = 3
        
        if keys[pygame.K_r]: 
            self.request_reload = True
        # Action Key Triggers
        if keys[pygame.K_r]: 
            self.request_reload = True
            
        # GRENADE SINGLE-AUTO IMPLEMENTATION:
        # Check if G is pressed this frame, and ensure it wasn't held down in the previous frame
        if keys[pygame.K_g]:
            if not hasattr(self, "grenade_button_held") or not self.grenade_button_held:
                self.request_grenade = True
                m_x, m_y = pygame.mouse.get_pos()
                self.grenade_target_vec = pygame.Vector2(m_x - self.pos.x, m_y - self.pos.y)
                self.grenade_button_held = True # Lock weapon firing loop
        else:
            self.grenade_button_held = False # Unlock once player releases the G key


    def update(self, dt: float, walls: list):
        self.pos.x += self.velocity.x * dt
        self.rect.x = int(self.pos.x - self.size//2)
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity.x > 0: self.pos.x = wall.rect.left - self.size//2
                elif self.velocity.x < 0: self.pos.x = wall.rect.right + self.size//2
                self.rect.x = int(self.pos.x - self.size//2)

        self.pos.y += self.velocity.y * dt
        self.rect.y = int(self.pos.y - self.size//2)
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if self.velocity.y > 0: self.pos.y = wall.rect.top - self.size//2
                elif self.velocity.y < 0: self.pos.y = wall.rect.bottom + self.size//2
                self.rect.y = int(self.pos.y - self.size//2)

        mouse_x, mouse_y = pygame.mouse.get_pos()
        self.angle = math.degrees(math.atan2(mouse_y - self.pos.y, mouse_x - self.pos.x))

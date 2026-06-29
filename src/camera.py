import pygame
import random


class Camera:

    def __init__(self):

        self.offset = pygame.Vector2()

        self.target = pygame.Vector2()

        self.shake_timer = 0

        self.shake_strength = 0

        self.zoom = 1.0

        self.recoil = pygame.Vector2()
    
    def update(self, dt, target):

        self.recoil *= 0.85

        self.target.update(target)

        self.offset += (self.target - self.offset) * 8 * dt

        if self.shake_timer > 0:

            self.shake_timer -= dt

            if self.shake_timer < 0:

                self.shake_timer = 0
        
    def shake(self, duration=0.15, strength=6):

        self.shake_timer = duration

        self.shake_strength = strength
    
    def get_offset(self):

        shake = pygame.Vector2()

        if self.shake_timer > 0:

            shake.x = random.randint(
                -self.shake_strength,
                self.shake_strength
            )

            shake.y = random.randint(
                -self.shake_strength,
                self.shake_strength
            )

        return self.offset + self.recoil + shake

    def kick(self, x, y):

        self.recoil.x += x

        self.recoil.y += y
    
    def set_zoom(self, zoom):

        self.zoom = zoom
        
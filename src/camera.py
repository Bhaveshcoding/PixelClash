import random
from typing import Optional

import pygame

from constants import HEIGHT, WIDTH


class Camera:
    """Simple camera controller with shake, recoil, and zoom support."""

    def __init__(self) -> None:
        self.offset: pygame.Vector2 = pygame.Vector2()
        self.target: pygame.Vector2 = pygame.Vector2()
        self.shake_timer: float = 0.0
        self.shake_strength: int = 0
        self.zoom: float = 1.0
        self.recoil: pygame.Vector2 = pygame.Vector2()

    def update(self, dt: float, target: pygame.Vector2) -> None:
        """Advance the camera towards the provided target."""
        self.recoil *= 0.85
        self.target.update(target)

        desired = pygame.Vector2(target.x - WIDTH / 2, target.y - HEIGHT / 2)
        self.offset += (desired - self.offset) * 8 * dt

        if self.shake_timer > 0.0:
            self.shake_timer -= dt
            if self.shake_timer < 0.0:
                self.shake_timer = 0.0

    def shake(self, duration: float = 0.15, strength: int = 6) -> None:
        """Apply screen shake for a short duration."""
        self.shake_timer = duration
        self.shake_strength = strength

    def get_offset(self) -> pygame.Vector2:
        """Return the current camera offset including recoil and shake."""
        shake = pygame.Vector2()
        if self.shake_timer > 0.0:
            shake.x = random.randint(-self.shake_strength, self.shake_strength)
            shake.y = random.randint(-self.shake_strength, self.shake_strength)
        return self.offset + self.recoil + shake

    def kick(self, x: float, y: float) -> None:
        """Apply a recoil kick to the camera."""
        self.recoil.x += x
        self.recoil.y += y

    def set_zoom(self, zoom: float) -> None:
        """Set the zoom value for the camera."""
        self.zoom = zoom
        
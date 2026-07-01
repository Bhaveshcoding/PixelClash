import math
import random
from typing import List, Sequence, Tuple

import pygame


class Particle:
    """A single particle with simple motion and fading behavior."""

    def __init__(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        velocity: Tuple[float, float],
        size: float,
        lifetime: float,
        gravity: float = 0.0,
        drag: float = 0.0,
        rotation: float = 0.0,
        rotation_speed: float = 0.0,
        fade: bool = True,
        shrink: bool = True,
    ) -> None:
        self.pos = pygame.Vector2(x, y)
        self.vel = pygame.Vector2(velocity)
        self.color = color
        self.size = size
        self.start_size = size
        self.life = lifetime
        self.max_life = lifetime
        self.gravity = gravity
        self.drag = drag
        self.rotation = rotation
        self.rotation_speed = rotation_speed
        self.fade = fade
        self.shrink = shrink

    def update(self, dt: float) -> bool:
        """Advance the particle state and return whether it is still alive."""
        self.life -= dt
        if self.life <= 0:
            return False

        self.vel.y += self.gravity * dt
        self.vel *= 1 - self.drag * dt
        self.pos += self.vel * dt
        self.rotation += self.rotation_speed * dt

        if self.shrink:
            ratio = self.life / self.max_life
            self.size = max(1.0, self.start_size * ratio)

        return True

    def draw(self, screen: pygame.Surface) -> None:
        """Render the particle to the provided surface."""
        alpha = 255 if not self.fade else int(255 * self.life / self.max_life)
        surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*self.color, alpha), (int(self.size), int(self.size)), int(self.size))
        surf = pygame.transform.rotate(surf, self.rotation)
        rect = surf.get_rect(center=(self.pos.x, self.pos.y))
        screen.blit(surf, rect)


class ParticleManager:
    """Manager for short-lived visual particles."""

    def __init__(self) -> None:
        self.particles: List[Particle] = []

    def update(self, dt: float) -> None:
        """Update all particles and remove expired ones."""
        self.particles = [particle for particle in self.particles if particle.update(dt)]

    def draw(self, screen: pygame.Surface) -> None:
        """Render all active particles."""
        for particle in self.particles:
            particle.draw(screen)

    def spawn(
        self,
        x: float,
        y: float,
        color: Tuple[int, int, int],
        count: int,
        speed: Sequence[float],
        size: Sequence[float],
        lifetime: Sequence[float],
        gravity: float = 0.0,
        drag: float = 0.0,
    ) -> None:
        """Spawn a burst of particles around the given position."""
        for _ in range(count):
            angle = random.uniform(0.0, math.pi * 2)
            velocity = (
                math.cos(angle) * random.uniform(*speed),
                math.sin(angle) * random.uniform(*speed),
            )
            self.particles.append(
                Particle(
                    x,
                    y,
                    color,
                    velocity,
                    random.uniform(*size),
                    random.uniform(*lifetime),
                    gravity,
                    drag,
                    random.uniform(0.0, 360.0),
                    random.uniform(-180.0, 180.0),
                )
            )

    def spawn_explosion(self, x: float, y: float) -> None:
        """Spawn an explosion particle burst."""
        self.spawn(x, y, (255, 120, 0), 40, (150.0, 400.0), (3.0, 8.0), (0.4, 0.8), gravity=200.0, drag=1.5)

    def spawn_muzzle_flash(self, x: float, y: float) -> None:
        """Spawn a muzzle flash particle burst."""
        self.spawn(x, y, (255, 230, 120), 10, (40.0, 120.0), (2.0, 5.0), (0.1, 0.2))

    def spawn_bullet_impact(self, x: float, y: float) -> None:
        """Spawn a bullet impact particle burst."""
        self.spawn(x, y, (220, 220, 220), 15, (50.0, 180.0), (2.0, 4.0), (0.2, 0.5), gravity=120.0)

    def spawn_dash(self, x: float, y: float) -> None:
        """Spawn a dash particle burst."""
        self.spawn(x, y, (180, 180, 180), 20, (20.0, 60.0), (3.0, 6.0), (0.5, 1.0), gravity=-30.0)

    def spawn_pickup(self, x: float, y: float) -> None:
        """Spawn a pickup particle burst."""
        self.spawn(x, y, (100, 255, 180), 18, (20.0, 100.0), (3.0, 6.0), (0.3, 0.7))

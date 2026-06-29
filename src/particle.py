import pygame
import random
import math


class Particle:

    # STEP 2
    def __init__(
        self,
        x,
        y,
        color,
        velocity,
        size,
        lifetime,
        gravity=0,
        drag=0,
        rotation=0,
        rotation_speed=0,
        fade=True,
        shrink=True
    ):

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


    # ----------------------------
    # STEP 3 GOES HERE
    # ----------------------------

    def update(self, dt):

        self.life -= dt

        if self.life <= 0:
            return False

        self.vel.y += self.gravity * dt

        self.vel *= (1 - self.drag * dt)

        self.pos += self.vel * dt

        self.rotation += self.rotation_speed * dt

        if self.shrink:

            ratio = self.life / self.max_life

            self.size = max(
                1,
                self.start_size * ratio
            )

        return True


    # ----------------------------
    # STEP 4 GOES HERE
    # ----------------------------

    def draw(self, screen):

        alpha = 255

        if self.fade:
            alpha = int(
                255 * self.life / self.max_life
            )

        surf = pygame.Surface(
            (int(self.size * 2), int(self.size * 2)),
            pygame.SRCALPHA
        )

        pygame.draw.circle(
            surf,
            (*self.color, alpha),
            (int(self.size), int(self.size)),
            int(self.size)
        )

        surf = pygame.transform.rotate(
            surf,
            self.rotation
        )

        rect = surf.get_rect(
            center=(self.pos.x, self.pos.y)
        )

        screen.blit(
            surf,
            rect
        )


# ==========================================
# STEP 5 STARTS HERE
# ==========================================

class ParticleManager:

    def __init__(self):
        self.particles = []

    def update(self, dt):

        self.particles = [

            p

            for p in self.particles

            if p.update(dt)

        ]
    def draw(self, screen):

        for p in self.particles:

            p.draw(screen)
    def spawn(
        self,
        x,
        y,
        color,
        count,
        speed,
        size,
        lifetime,
        gravity=0,
        drag=0,
    ):

        for _ in range(count):

            angle = random.uniform(
                0,
                math.pi * 2
            )

            velocity = (

                math.cos(angle) * random.uniform(*speed),

                math.sin(angle) * random.uniform(*speed)

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

                    random.uniform(0,360),

                    random.uniform(-180,180)

                )

            )
    def spawn_explosion(self, x, y):

        self.spawn(
            x,
            y,
            (255, 120, 0),
            40,
            (150, 400),
            (3, 8),
            (0.4, 0.8),
            gravity=200,
            drag=1.5
        )


    def spawn_muzzle_flash(self, x, y):

        self.spawn(
            x,
            y,
            (255, 230, 120),
            10,
            (40, 120),
            (2, 5),
            (0.1, 0.2)
        )


    def spawn_bullet_impact(self, x, y):

        self.spawn(
            x,
            y,
            (220, 220, 220),
            15,
            (50, 180),
            (2, 4),
            (0.2, 0.5),
            gravity=120
        )


    def spawn_dash(self, x, y):

        self.spawn(
            x,
            y,
            (180, 180, 180),
            20,
            (20, 60),
            (3, 6),
            (0.5, 1.0),
            gravity=-30
        )


    def spawn_pickup(self, x, y):

        self.spawn(
            x,
            y,
            (100, 255, 180),
            18,
            (20, 100),
            (2, 5),
            (0.3, 0.7)
        )
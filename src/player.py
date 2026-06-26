import pygame
from constants import PLAYER_SIZE, PLAYER_SPEED, PLAYER_COLOR, SPAWN_POINTS

class Player:
    def __init__(self):
        # Pull initial position coordinate safely from Spawn Point A
        start_x, start_y = SPAWN_POINTS[0]
        self.pos = pygame.Vector2(start_x, start_y)
        
        self.size = PLAYER_SIZE
        self.speed = PLAYER_SPEED
        self.velocity = pygame.Vector2(0, 0)
        
        # Construct the rendering rectangle
        self.surface = pygame.Surface((self.size, self.size))
        self.surface.fill(PLAYER_COLOR)
        self.rect = self.surface.get_rect()
        self.rect.topleft = (int(self.pos.x), int(self.pos.y))

    def handle_input(self):
        """Reads keyboard inputs to modify velocity vector."""
        keys = pygame.key.get_pressed()
        self.velocity.x = 0
        self.velocity.y = 0

        if keys[pygame.K_w]: self.velocity.y -= 1
        if keys[pygame.K_s]: self.velocity.y += 1
        if keys[pygame.K_a]: self.velocity.x -= 1
        if keys[pygame.K_d]: self.velocity.x += 1

        # Prevent diagonal speed boost
        if self.velocity.length_squared() > 0:
            self.velocity = self.velocity.normalize() * self.speed

    def update(self, dt: float, walls: list):
        """Separates Axis-Aligned calculations to allow clean sliding motion."""
        # 1. Calculate and check horizontal changes
        self.pos.x += self.velocity.x * dt
        self.rect.x = int(self.pos.x)
        self.process_collisions(walls, axis='x')

        # 2. Calculate and check vertical changes
        self.pos.y += self.velocity.y * dt
        self.rect.y = int(self.pos.y)
        self.process_collisions(walls, axis='y')

    def process_collisions(self, walls: list, axis: str):
        """Resolves overlapping boundaries on the active coordinate axis."""
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                if axis == 'x':
                    if self.velocity.x > 0:  # Heading Right
                        self.rect.right = wall.rect.left
                    elif self.velocity.x < 0:  # Heading Left
                        self.rect.left = wall.rect.right
                    self.pos.x = float(self.rect.x)
                    
                elif axis == 'y':
                    if self.velocity.y > 0:  # Heading Down
                        self.rect.bottom = wall.rect.top
                    elif self.velocity.y < 0:  # Heading Up
                        self.rect.top = wall.rect.bottom
                    self.pos.y = float(self.rect.y)

    def draw(self, surface: pygame.Surface):
        """Renders the player box onto the active surface."""
        surface.blit(self.surface, self.rect)

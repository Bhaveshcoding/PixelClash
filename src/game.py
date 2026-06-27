import sys
import pygame
from constants import WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, WALL_LAYOUTS, CROSSHAIR_COLOR
from player import Player
from wall import Wall

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        # Hide standard desktop arrow cursor
        pygame.mouse.set_visible(False)
        
        # Core Staging Environments
        self.player = Player()
        self.walls = []
        self.bullets = []
        
        self.build_arena()

    def build_arena(self):
        for item in WALL_LAYOUTS:
            x, y, w, h = item
            self.walls.append(Wall(x, y, w, h))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.is_running = False

        # Continuous Input Polling for Shooting (Left Click)
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]: # Left Mouse Button Down
            if self.player.can_shoot():
                new_bullet = self.player.shoot()
                self.bullets.append(new_bullet)

    def update(self, dt: float):
        # 1. Update entities
        self.player.handle_input()
        self.player.update(dt, self.walls)
        
        for bullet in self.bullets:
            bullet.update(dt)
            
        # 2. Process Bullet Collisions against Wall blocks
        for bullet in self.bullets[:]:
            # Remove bullets that hit walls
            for wall in self.walls:
                if bullet.rect.colliderect(wall.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break
                    
            # Remove bullets whose lifetimes have run out
            if bullet in self.bullets and bullet.is_dead():
                self.bullets.remove(bullet)

    def draw_crosshair(self):
        """Draws a custom crosshair circle directly at the mouse coordinates."""
        m_pos = pygame.mouse.get_pos()
        # Convert position to Vector2 for easier coordinate arithmetic
        m_vec = pygame.Vector2(m_pos)
        pygame.draw.circle(self.screen, CROSSHAIR_COLOR, m_pos, 8, 2)
        pygame.draw.line(self.screen, CROSSHAIR_COLOR, (m_vec.x - 12, m_vec.y), (m_vec.x + 12, m_vec.y), 2)
        pygame.draw.line(self.screen, CROSSHAIR_COLOR, (m_vec.x, m_vec.y - 12), (m_vec.x, m_vec.y + 12), 2)

    def draw(self):
        # Enforce exact layer sequence drawing:
        # Background -> Walls -> Bullets -> Player -> Custom UI/Crosshair
        self.screen.fill(BACKGROUND_COLOR)
        
        for wall in self.walls:
            wall.draw(self.screen)
            
        for bullet in self.bullets:
            bullet.draw(self.screen)
            
        self.player.draw(self.screen)
        
        # Render the custom crosshair on top of all other elements
        self.draw_crosshair()
        
        pygame.display.flip()

    def run(self):
        while self.is_running:
            self.handle_events()
            dt = self.clock.tick(FPS) / 1000.0
            self.update(dt)
            self.draw()
            
        pygame.quit()
        sys.exit()

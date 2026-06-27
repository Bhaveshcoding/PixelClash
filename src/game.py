import sys
import pygame
from constants import (
    WIDTH, HEIGHT, FPS, TITLE, BACKGROUND_COLOR, 
    WALL_LAYOUTS, CROSSHAIR_COLOR, UI_COLOR, DUMMY_COLOR
)
from player import Player
from wall import Wall

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.is_running = True
        
        pygame.mouse.set_visible(False)
        self.ui_font = pygame.font.SysFont(None, 36)
        self.win_font = pygame.font.SysFont(None, 72)
        self.match_over = False
        self.winner_name = ""

        # Players initialization (Index 0 = Host Local, Index 1 = Dummy Opponent for target testing)
        self.player = Player(spawn_index=0, name="Player 1")
        self.dummy = Player(spawn_index=1, color=DUMMY_COLOR, name="Target Dummy")
        
        self.players_list = [self.player, self.dummy]
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
                # Allow manual match restart once a victory screen is active
                if self.match_over and event.key == pygame.K_SPACE:
                    self.reset_match()

        if self.match_over:
            return

        # Local Player Left Click Firing loop
        mouse_buttons = pygame.mouse.get_pressed()
        if mouse_buttons[0]: 
            if self.player.can_shoot():
                self.bullets.append(self.player.shoot())

        # Target Dummy AI behavior: Periodically track and shoot back towards the player
        if self.dummy.is_alive and self.player.is_alive:
            self.dummy.update_aim(target_pos=self.player.pos)
            # Give dummy slower firing rate behavior
            if self.dummy.can_shoot() and pygame.time.get_ticks() % 10 < 2:
                self.bullets.append(self.dummy.shoot(target_pos=self.player.pos))

    def reset_match(self):
        self.match_over = False
        self.winner_name = ""
        for p in self.players_list:
            p.kills = 0
            p.deaths = 0
            p.reset_to_spawn()
        self.bullets.clear()

    def update(self, dt: float):
        if self.match_over:
            return

        # 1. Update entities
        self.player.handle_input()
        self.player.update_aim()
        
        for p in self.players_list:
            p.update(dt, self.walls)
            
        for bullet in self.bullets:
            bullet.update(dt)

        # 2. Check Bullet Collisions against Players and Walls
        for bullet in self.bullets[:]:
            bullet_removed = False
            
            # Check against Wall obstacles
            for wall in self.walls:
                if bullet.rect.colliderect(wall.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    bullet_removed = True
                    break
            if bullet_removed:
                continue

            # Check against Players
            for target in self.players_list:
                # Do not hit yourself or dead entities
                if bullet.owner == target or not target.is_alive:
                    continue
                    
                if bullet.rect.colliderect(target.rect):
                    # Apply constant bullet damage
                    from constants import BULLET_DAMAGE
                    was_killed = target.take_damage(BULLET_DAMAGE)
                    
                    if was_killed and bullet.owner:
                        bullet.owner.kills += 1
                        # Instantly check victory threshold matching rule
                        if bullet.owner.kills >= 10:
                            self.match_over = True
                            self.winner_name = bullet.owner.name

                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    break

            # Despawn long-distance bullets
            if bullet in self.bullets and bullet.is_dead():
                self.bullets.remove(bullet)

    def draw_ui(self):
        """Draws score tracking overlays on screen corner viewspaces."""
        # Print Local Player Statistics top-left
        stats_txt = self.ui_font.render(f"Kills: {self.player.kills} | Deaths: {self.player.deaths}", True, UI_COLOR)
        self.screen.blit(stats_txt, (30, 30))
        
        # Print Target Dummy Statistics top-right
        dummy_txt = self.ui_font.render(f"Enemy Kills: {self.dummy.kills}", True, DUMMY_COLOR)
        self.screen.blit(dummy_txt, (WIDTH - 240, 30))

        # Render Victory layout cover if game terminates
        if self.match_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180)) # Dim the background canvas dark transparent
            self.screen.blit(overlay, (0, 0))
            
            win_txt = self.win_font.render(f"{self.winner_name} WINS THE CLASH!", True, UI_COLOR)
            sub_txt = self.ui_font.render("Press SPACE to reset the arena match", True, UI_COLOR)
            
            self.screen.blit(win_txt, (WIDTH // 2 - win_txt.get_width() // 2, HEIGHT // 2 - 50))
            self.screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2 + 30))

    def draw_crosshair(self):
        m_pos = pygame.mouse.get_pos()
        m_vec = pygame.Vector2(m_pos)
        pygame.draw.circle(self.screen, CROSSHAIR_COLOR, m_pos, 8, 2)
        pygame.draw.line(self.screen, CROSSHAIR_COLOR, (m_vec.x - 12, m_vec.y), (m_vec.x + 12, m_vec.y), 2)
        pygame.draw.line(self.screen, CROSSHAIR_COLOR, (m_vec.x, m_vec.y - 12), (m_vec.x, m_vec.y + 12), 2)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        
        for wall in self.walls:
            wall.draw(self.screen)
            
        for bullet in self.bullets:
            bullet.draw(self.screen)
            
        for p in self.players_list:
            p.draw(self.screen)
            
        self.draw_ui()
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

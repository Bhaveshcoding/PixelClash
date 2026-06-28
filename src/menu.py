import pygame
from constants import WIDTH, HEIGHT, BACKGROUND_COLOR, UI_COLOR

class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont(None, 80)
        self.font_btn = pygame.font.SysFont(None, 48)
        self.font_sm = pygame.font.SysFont(None, 32)
        
        # Connection Variables
        self.ip_input_text = "127.0.0.1"
        self.input_active = False
        
        # New Settings Variables
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.is_fullscreen = False
        self.show_fps = True

    def draw_main_menu(self) -> str:
        """Renders main screen elements and returns interaction commands."""
        self.screen.fill(BACKGROUND_COLOR)
        t_surf = self.font_title.render("PIXEL CLASH", True, (0, 200, 255))
        self.screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 100))

        # Build Button Boxes
        btn_host = pygame.Rect(WIDTH//2 - 150, 240, 300, 50)
        btn_join = pygame.Rect(WIDTH//2 - 150, 320, 300, 50)
        btn_sett = pygame.Rect(WIDTH//2 - 150, 400, 300, 50) # New settings button
        btn_quit = pygame.Rect(WIDTH//2 - 150, 480, 300, 50)

        m_pos = pygame.mouse.get_pos()
        buttons = [(btn_host, "HOST GAME"), (btn_join, "JOIN GAME"), (btn_sett, "SETTINGS"), (btn_quit, "QUIT")]
        
        for r, text in buttons:
            color = (100, 100, 120) if r.collidepoint(m_pos) else (50, 50, 60)
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            txt = self.font_btn.render(text, True, UI_COLOR)
            self.screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

        if pygame.mouse.get_pressed()[0]:
            pygame.time.delay(150)
            if btn_host.collidepoint(m_pos): return "HOST"
            if btn_join.collidepoint(m_pos): return "JOIN_SCREEN"
            if btn_sett.collidepoint(m_pos): return "SETTINGS"
            if btn_quit.collidepoint(m_pos): return "QUIT"
        return "MAIN_MENU"

    def draw_settings_screen(self) -> str:
        """Renders interactive settings panel for full controls configuration."""
        self.screen.fill(BACKGROUND_COLOR)
        m_pos = pygame.mouse.get_pos()
        m_click = pygame.mouse.get_pressed()[0]

        lbl = self.font_title.render("SETTINGS", True, UI_COLOR)
        self.screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 80))

        # 1. Music Volume Slider UI
        m_lbl = self.font_sm.render(f"Music Volume: {int(self.music_volume * 100)}%", True, UI_COLOR)
        self.screen.blit(m_lbl, (WIDTH//2 - 200, 200))
        m_slider = pygame.Rect(WIDTH//2 - 200, 230, 400, 10)
        pygame.draw.rect(self.screen, (60, 60, 70), m_slider)
        if m_click and m_slider.inflate(0, 20).collidepoint(m_pos):
            self.music_volume = max(0.0, min(1.0, (m_pos[0] - m_slider.x) / m_slider.width))
        pygame.draw.circle(self.screen, (0, 200, 255), (int(m_slider.x + self.music_volume * m_slider.width), m_slider.centery), 10)

        # 2. SFX Volume Slider UI
        s_lbl = self.font_sm.render(f"SFX Volume: {int(self.sfx_volume * 100)}%", True, UI_COLOR)
        self.screen.blit(s_lbl, (WIDTH//2 - 200, 270))
        s_slider = pygame.Rect(WIDTH//2 - 200, 300, 400, 10)
        pygame.draw.rect(self.screen, (60, 60, 70), s_slider)
        if m_click and s_slider.inflate(0, 20).collidepoint(m_pos):
            self.sfx_volume = max(0.0, min(1.0, (m_pos[0] - s_slider.x) / s_slider.width))
        pygame.draw.circle(self.screen, (0, 200, 255), (int(s_slider.x + self.sfx_volume * s_slider.width), s_slider.centery), 10)

        # 3. Fullscreen Checkbox UI
        fs_lbl = self.font_sm.render("Fullscreen Mode", True, UI_COLOR)
        self.screen.blit(fs_lbl, (WIDTH//2 - 200, 350))
        fs_box = pygame.Rect(WIDTH//2 + 100, 350, 25, 25)
        pygame.draw.rect(self.screen, (50, 50, 60), fs_box, border_radius=4)
        if self.is_fullscreen:
            pygame.draw.rect(self.screen, (0, 200, 255), fs_box.inflate(-6, -6), border_radius=2)
        if m_click and fs_box.collidepoint(m_pos):
            pygame.time.delay(150)
            self.is_fullscreen = not self.is_fullscreen
            return "TOGGLE_FULLSCREEN"

        # 4. FPS Display Checkbox UI
        fps_lbl = self.font_sm.render("Show FPS Counter", True, UI_COLOR)
        self.screen.blit(fps_lbl, (WIDTH//2 - 200, 400))
        fps_box = pygame.Rect(WIDTH//2 + 100, 400, 25, 25)
        pygame.draw.rect(self.screen, (50, 50, 60), fps_box, border_radius=4)
        if self.show_fps:
            pygame.draw.rect(self.screen, (0, 200, 255), fps_box.inflate(-6, -6), border_radius=2)
        if m_click and fps_box.collidepoint(m_pos):
            pygame.time.delay(150)
            self.show_fps = not self.show_fps

        # Back Button
        btn_back = pygame.Rect(WIDTH//2 - 150, 480, 300, 50)
        c = (100, 100, 120) if btn_back.collidepoint(m_pos) else (50, 50, 60)
        pygame.draw.rect(self.screen, c, btn_back, border_radius=8)
        t = self.font_btn.render("BACK", True, UI_COLOR)
        self.screen.blit(t, (btn_back.centerx - t.get_width()//2, btn_back.centery - t.get_height()//2))

        if m_click and btn_back.collidepoint(m_pos):
            pygame.time.delay(150)
            return "MAIN_MENU"

        return "SETTINGS"

    def draw_join_screen(self) -> tuple:
        self.screen.fill(BACKGROUND_COLOR)
        lbl = self.font_title.render("ENTER HOST IP", True, UI_COLOR)
        self.screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 150))

        input_box = pygame.Rect(WIDTH//2 - 200, 280, 400, 50)
        box_color = (0, 200, 255) if self.input_active else (100, 100, 100)
        pygame.draw.rect(self.screen, (20, 20, 25), input_box)
        pygame.draw.rect(self.screen, box_color, input_box, 3, border_radius=5)

        txt = self.font_btn.render(self.ip_input_text, True, UI_COLOR)
        self.screen.blit(txt, (input_box.x + 15, input_box.centery - txt.get_height()//2))

        btn_conn = pygame.Rect(WIDTH//2 - 150, 380, 300, 50)
        btn_back = pygame.Rect(WIDTH//2 - 150, 460, 300, 50)

        m_pos = pygame.mouse.get_pos()
        for r, text in [(btn_conn, "CONNECT"), (btn_back, "BACK")]:
            c = (100, 100, 120) if r.collidepoint(m_pos) else (50, 50, 60)
            pygame.draw.rect(self.screen, c, r, border_radius=8)
            t = self.font_btn.render(text, True, UI_COLOR)
            self.screen.blit(t, (r.centerx - t.get_width()//2, r.centery - t.get_height()//2))

        if pygame.mouse.get_pressed()[0]:
            pygame.time.delay(150)
            if input_box.collidepoint(m_pos):
                self.input_active = True
            else:
                self.input_active = False
                if btn_conn.collidepoint(m_pos): return "CONNECT_ACTION", self.ip_input_text
                if btn_back.collidepoint(m_pos): return "MAIN_MENU", ""
        return "JOIN_SCREEN", ""

    def handle_keyboard_input(self, event):
        if self.input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.ip_input_text = self.ip_input_text[:-1]
            elif event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                self.input_active = False
            else:
                if len(self.ip_input_text) < 15 and event.unicode in "0123456789.":
                    self.ip_input_text += event.unicode

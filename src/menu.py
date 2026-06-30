import pygame
from constants import WIDTH, HEIGHT, BACKGROUND_COLOR, UI_COLOR

class MenuSystem:
    def __init__(self, screen):
        self.screen = screen
        self.font_title = pygame.font.SysFont("Impact", 80)
        self.font_btn = pygame.font.SysFont("Arial", 28, bold=True)
        self.font_sm = pygame.font.SysFont("Arial", 22, bold=True)
        
        # Connection Paths
        self.ip_input_text = "127.0.0.1"
        self.input_active = False
        
        # Menu Selection Settings Configuration Profiles
        self.music_volume = 0.5
        self.sfx_volume = 0.5
        self.is_fullscreen = False
        self.show_fps = True
        self.profile_dirty = False
        self.history_scroll = 0
        self.career_scroll = 0
        
        # Single-Click Event Tracking Triggers
        self.mouse_was_pressed = False
        self.click_registered = False

    def update_clicks(self):
        """Processes an event-driven click edge toggle check to isolate input ticks."""
        current_click = pygame.mouse.get_pressed()[0]
        if current_click and not self.mouse_was_pressed:
            self.click_registered = True
        else:
            self.click_registered = False
        self.mouse_was_pressed = current_click

    def draw_main_menu(self) -> str:
        self.update_clicks()
        self.screen.fill(BACKGROUND_COLOR)
        t_surf = self.font_title.render("PIXEL CLASH", True, (0, 200, 255))
        self.screen.blit(t_surf, (WIDTH//2 - t_surf.get_width()//2, 100))

        btn_host = pygame.Rect(WIDTH//2 - 150, 180, 300, 50)
        btn_join = pygame.Rect(WIDTH//2 - 150, 245, 300, 50)
        btn_sett = pygame.Rect(WIDTH//2 - 150, 310, 300, 50) 
        btn_ach = pygame.Rect(WIDTH//2 - 150, 375, 300, 50)
        btn_hist = pygame.Rect(WIDTH//2 - 150, 440, 300, 50)
        btn_stats = pygame.Rect(WIDTH//2 - 150, 505, 300, 50)
        btn_quit = pygame.Rect(WIDTH//2 - 150, 570, 300, 50)

        m_pos = pygame.mouse.get_pos()
        buttons = [(btn_host, "HOST GAME"), (btn_join, "JOIN GAME"), (btn_sett, "SETTINGS"), (btn_ach, "ACHIEVEMENTS"), (btn_hist, "MATCH HISTORY"), (btn_stats, "CAREER STATS"), (btn_quit, "QUIT")]
        
        for r, text in buttons:
            color = (100, 100, 120) if r.collidepoint(m_pos) else (50, 50, 60)
            pygame.draw.rect(self.screen, color, r, border_radius=8)
            txt = self.font_btn.render(text, True, UI_COLOR)
            self.screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

        if self.click_registered:
            if btn_host.collidepoint(m_pos): return "HOST"
            if btn_join.collidepoint(m_pos): return "JOIN_SCREEN"
            if btn_sett.collidepoint(m_pos): return "SETTINGS"
            if btn_ach.collidepoint(m_pos): return "ACHIEVEMENTS"
            if btn_hist.collidepoint(m_pos): return "MATCH_HISTORY"
            if btn_stats.collidepoint(m_pos): return "CAREER_STATS"
            if btn_quit.collidepoint(m_pos): return "QUIT"
        return "MAIN_MENU"

    def draw_settings_screen(self) -> str:
        """Renders settings menu using event-driven clicks to prevent multi-triggering bugs."""
        self.update_clicks()
        self.screen.fill(BACKGROUND_COLOR)
        m_pos = pygame.mouse.get_pos()
        m_hold = pygame.mouse.get_pressed()[0]

        lbl = self.font_title.render("SETTINGS", True, UI_COLOR)
        self.screen.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 80))

        # 1. Music Volume Bar UI Layout (Polled smoothly on down-hold)
        m_lbl = self.font_sm.render(f"Music Volume: {int(self.music_volume * 100)}%", True, UI_COLOR)
        self.screen.blit(m_lbl, (WIDTH//2 - 200, 180))
        m_slider = pygame.Rect(WIDTH//2 - 200, 210, 400, 10)
        pygame.draw.rect(self.screen, (60, 60, 70), m_slider)
        if m_hold and m_slider.inflate(0, 20).collidepoint(m_pos):
            self.music_volume = max(0.0, min(1.0, (m_pos[0] - m_slider.x) / m_slider.width))
            self.profile_dirty = True
        pygame.draw.circle(self.screen, (0, 200, 255), (int(m_slider.x + self.music_volume * m_slider.width), m_slider.centery), 10)

        # 2. SFX Volume Bar UI Layout (Polled smoothly on down-hold)
        s_lbl = self.font_sm.render(f"SFX Volume: {int(self.sfx_volume * 100)}%", True, UI_COLOR)
        self.screen.blit(s_lbl, (WIDTH//2 - 200, 250))
        s_slider = pygame.Rect(WIDTH//2 - 200, 280, 400, 10)
        pygame.draw.rect(self.screen, (60, 60, 70), s_slider)
        if m_hold and s_slider.inflate(0, 20).collidepoint(m_pos):
            self.sfx_volume = max(0.0, min(1.0, (m_pos[0] - s_slider.x) / s_slider.width))
            self.profile_dirty = True
        pygame.draw.circle(self.screen, (0, 200, 255), (int(s_slider.x + self.sfx_volume * s_slider.width), s_slider.centery), 10)

        # 3. Fullscreen Checkbox UI Layout (Fires cleanly on click edge)
        fs_lbl = self.font_sm.render("Fullscreen Mode", True, UI_COLOR)
        self.screen.blit(fs_lbl, (WIDTH//2 - 200, 330))
        fs_box = pygame.Rect(WIDTH//2 + 100, 330, 25, 25)
        pygame.draw.rect(self.screen, (50, 50, 60), fs_box, border_radius=4)
        if self.is_fullscreen:
            pygame.draw.rect(self.screen, (0, 200, 255), fs_box.inflate(-6, -6), border_radius=2)

        # 4. Show FPS Checkbox UI Layout (Fires cleanly on click edge)
        fps_lbl = self.font_sm.render("Show FPS Counter", True, UI_COLOR)
        self.screen.blit(fps_lbl, (WIDTH//2 - 200, 380))
        fps_box = pygame.Rect(WIDTH//2 + 100, 380, 25, 25)
        pygame.draw.rect(self.screen, (50, 50, 60), fps_box, border_radius=4)
        if self.show_fps:
            pygame.draw.rect(self.screen, (0, 200, 255), fps_box.inflate(-6, -6), border_radius=2)

        # 5. Back Navigation Button
        btn_back = pygame.Rect(WIDTH//2 - 150, 460, 300, 50)
        c = (100, 100, 120) if btn_back.collidepoint(m_pos) else (50, 50, 60)
        pygame.draw.rect(self.screen, c, btn_back, border_radius=8)
        t = self.font_btn.render("BACK", True, UI_COLOR)
        self.screen.blit(t, (btn_back.centerx - t.get_width()//2, btn_back.centery - t.get_height()//2))

        # Handle Click Edge Processing Actions
        if self.click_registered:
            if fs_box.collidepoint(m_pos):
                self.is_fullscreen = not self.is_fullscreen
                self.profile_dirty = True
                return "TOGGLE_FULLSCREEN"
            if fps_box.collidepoint(m_pos):
                self.show_fps = not self.show_fps
                self.profile_dirty = True
            if btn_back.collidepoint(m_pos):
                return "MAIN_MENU"

        return "SETTINGS"

    def draw_achievements_screen(self, achievements) -> str:
        self.update_clicks()
        self.screen.fill(BACKGROUND_COLOR)
        title = self.font_title.render("ACHIEVEMENTS", True, UI_COLOR)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        achievements.draw_menu(self.screen, self.font_sm)
        btn_back = pygame.Rect(WIDTH//2 - 150, 520, 300, 50)
        m_pos = pygame.mouse.get_pos()
        c = (100, 100, 120) if btn_back.collidepoint(m_pos) else (50, 50, 60)
        pygame.draw.rect(self.screen, c, btn_back, border_radius=8)
        t = self.font_btn.render("BACK", True, UI_COLOR)
        self.screen.blit(t, (btn_back.centerx - t.get_width()//2, btn_back.centery - t.get_height()//2))
        if self.click_registered and btn_back.collidepoint(m_pos):
            return "MAIN_MENU"
        return "ACHIEVEMENTS"

    def draw_history_screen(self, history_manager) -> str:
        self.update_clicks()
        self.screen.fill(BACKGROUND_COLOR)
        title = self.font_title.render("MATCH HISTORY", True, UI_COLOR)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.history_scroll = max(0, self.history_scroll - 1)
        if keys[pygame.K_DOWN]:
            self.history_scroll += 1
        matches = history_manager.load_matches()
        start = self.history_scroll
        for idx, match in enumerate(matches[start:start + 8]):
            y = 150 + idx * 70
            winner = match.get("winner", "UNKNOWN")
            date = match.get("date", "")
            duration = match.get("duration", 0)
            players = match.get("players", {})
            kills = ", ".join(f"P{pid}:{p.get('kills',0)}" for pid,p in players.items())
            text = self.font_sm.render(f"{winner} | {date} | {duration}s | {kills}", True, UI_COLOR)
            self.screen.blit(text, (40, y))
        btn_back = pygame.Rect(WIDTH//2 - 150, 620, 300, 40)
        m_pos = pygame.mouse.get_pos()
        c = (100, 100, 120) if btn_back.collidepoint(m_pos) else (50, 50, 60)
        pygame.draw.rect(self.screen, c, btn_back, border_radius=8)
        t = self.font_btn.render("BACK", True, UI_COLOR)
        self.screen.blit(t, (btn_back.centerx - t.get_width()//2, btn_back.centery - t.get_height()//2))
        if self.click_registered and btn_back.collidepoint(m_pos):
            return "MAIN_MENU"
        return "MATCH_HISTORY"

    def draw_career_stats_screen(self, history_manager) -> str:
        self.update_clicks()
        self.screen.fill(BACKGROUND_COLOR)
        title = self.font_title.render("CAREER STATS", True, UI_COLOR)
        self.screen.blit(title, (WIDTH//2 - title.get_width()//2, 70))
        stats = history_manager.get_career_stats()
        lines = [
            f"Matches Played: {stats.get('matches_played', 0)}",
            f"Wins: {stats.get('wins', 0)}",
            f"Losses: {stats.get('losses', 0)}",
            f"Overall Accuracy: {stats.get('overall_accuracy', 0):.2f}%",
            f"Average Damage: {stats.get('average_damage', 0):.2f}",
            f"Average Survival Time: {stats.get('average_survival_time', 0):.2f}s",
            f"Highest Kill Streak: {stats.get('highest_kill_streak', 0)}",
            f"Average Kills: {stats.get('average_kills', 0):.2f}",
            f"Average Deaths: {stats.get('average_deaths', 0):.2f}",
        ]
        for idx, line in enumerate(lines):
            text = self.font_sm.render(line, True, UI_COLOR)
            self.screen.blit(text, (120, 180 + idx * 38))
        btn_back = pygame.Rect(WIDTH//2 - 150, 620, 300, 40)
        m_pos = pygame.mouse.get_pos()
        c = (100, 100, 120) if btn_back.collidepoint(m_pos) else (50, 50, 60)
        pygame.draw.rect(self.screen, c, btn_back, border_radius=8)
        t = self.font_btn.render("BACK", True, UI_COLOR)
        self.screen.blit(t, (btn_back.centerx - t.get_width()//2, btn_back.centery - t.get_height()//2))
        if self.click_registered and btn_back.collidepoint(m_pos):
            return "MAIN_MENU"
        return "CAREER_STATS"

    def draw_join_screen(self) -> tuple:
        self.update_clicks()
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

        if self.click_registered:
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

import os
import time
import pygame


class Achievement:
    def __init__(self, name, description, icon="🏆"):
        self.name = name
        self.description = description
        self.unlocked = False
        self.icon = icon
        self.unlock_time = None


class AchievementManager:
    def __init__(self):
        self.achievements = {
            "First Blood": Achievement("First Blood", "Get your first kill."),
            "Untouchable": Achievement("Untouchable", "Get 5 kills without dying."),
            "Sharpshooter": Achievement("Sharpshooter", "Reach 80% accuracy with at least 30 shots fired."),
            "Bomber": Achievement("Bomber", "Land at least one grenade hit."),
            "Collector": Achievement("Collector", "Collect at least 5 pickups."),
            "Destroyer": Achievement("Destroyer", "Destroy at least 10 crates."),
            "Survivor": Achievement("Survivor", "Win the match while having health below 20."),
            "Rampage": Achievement("Rampage", "Reach a kill streak of 10."),
        }
        self.notifications = []
        self._last_checked = None

    def unlock(self, name):
        if name in self.achievements and not self.achievements[name].unlocked:
            self.achievements[name].unlocked = True
            self.achievements[name].unlock_time = time.time()
            self.notifications.append({
                "name": name,
                "created_at": time.time(),
                "alpha": 255,
            })

    def check(self, player_stats, winner=None, health=None):
        stats = player_stats
        resolved_winner = winner
        if resolved_winner is None:
            resolved_winner = getattr(stats, "winner", False)
        resolved_health = health
        if resolved_health is None:
            resolved_health = getattr(stats, "health", 100)

        if getattr(stats, "kills", 0) >= 1:
            self.unlock("First Blood")
        if getattr(stats, "kills", 0) >= 5 and getattr(stats, "deaths", 0) == 0:
            self.unlock("Untouchable")
        if getattr(stats, "accuracy", 0) >= 80 and getattr(stats, "shots_fired", 0) >= 30:
            self.unlock("Sharpshooter")
        if getattr(stats, "grenade_hits", 0) >= 1:
            self.unlock("Bomber")
        if getattr(stats, "pickups_collected", 0) >= 5:
            self.unlock("Collector")
        if getattr(stats, "crates_destroyed", 0) >= 10:
            self.unlock("Destroyer")
        if resolved_winner and resolved_health < 20:
            self.unlock("Survivor")
        if getattr(stats, "longest_kill_streak", 0) >= 10:
            self.unlock("Rampage")
        self._last_checked = getattr(stats, "kills", 0)

    def reset(self):
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.unlock_time = None
        self.notifications = []

    def draw_notifications(self, surface, font):
        current_time = time.time()
        active = []
        for notification in self.notifications:
            age = current_time - notification["created_at"]
            if age < 3.0:
                alpha = int(max(0, 255 - (age / 3.0) * 255))
                notification["alpha"] = alpha
                active.append(notification)
        self.notifications = active

        x = surface.get_width() - 320
        y = 20
        for notification in self.notifications:
            text = f"🏆 ACHIEVEMENT\n{notification['name']}\nUnlocked"
            txt_surf = font.render(text, True, (255, 215, 0))
            alpha = notification["alpha"]
            if alpha <= 0:
                continue
            overlay = pygame.Surface(txt_surf.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, alpha // 2))
            surface.blit(overlay, (x, y))
            txt = font.render(text, True, (255, 215, 0))
            txt.set_alpha(alpha)
            surface.blit(txt, (x + 10, y + 8))
            y += 70

    def draw_menu(self, surface, font):
        surface.fill((20, 20, 25))
        title = font.render("ACHIEVEMENTS", True, (255, 215, 0))
        surface.blit(title, (20, 20))
        y = 90
        for name, achievement in self.achievements.items():
            status = "✓" if achievement.unlocked else "□"
            line = f"{status} {name}"
            text = font.render(line, True, (255, 255, 255) if achievement.unlocked else (180, 180, 180))
            surface.blit(text, (30, y))
            y += 30

import time
from typing import Dict, List, Optional, Any

import pygame


class Achievement:
    """Represents a single achievement entry."""

    def __init__(self, name: str, description: str, icon: str = "🏆") -> None:
        self.name = name
        self.description = description
        self.unlocked = False
        self.icon = icon
        self.unlock_time: Optional[float] = None


class AchievementManager:
    """Track and render achievements and unlock notifications."""

    def __init__(self) -> None:
        self.achievements: Dict[str, Achievement] = {
            "First Blood": Achievement("First Blood", "Get your first kill."),
            "Untouchable": Achievement("Untouchable", "Get 5 kills without dying."),
            "Sharpshooter": Achievement("Sharpshooter", "Reach 80% accuracy with at least 30 shots fired."),
            "Bomber": Achievement("Bomber", "Land at least one grenade hit."),
            "Collector": Achievement("Collector", "Collect at least 5 pickups."),
            "Destroyer": Achievement("Destroyer", "Destroy at least 10 crates."),
            "Survivor": Achievement("Survivor", "Win the match while having health below 20."),
            "Rampage": Achievement("Rampage", "Reach a kill streak of 10."),
        }
        self.notifications: List[Dict[str, Any]] = []
        self._last_checked: Optional[int] = None

    def unlock(self, name: str) -> None:
        """Unlock an achievement if it exists and is not already unlocked."""
        achievement = self.achievements.get(name)
        if achievement is None or achievement.unlocked:
            return

        achievement.unlocked = True
        achievement.unlock_time = time.time()
        self.notifications.append({"name": name, "created_at": time.time(), "alpha": 255})

    def check(self, player_stats: Any, winner: Optional[bool] = None, health: Optional[int] = None) -> None:
        """Evaluate gameplay stats and unlock any matching achievements."""
        stats = player_stats
        resolved_winner = winner if winner is not None else getattr(stats, "winner", False)
        resolved_health = health if health is not None else getattr(stats, "health", 100)

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

    def reset(self) -> None:
        """Reset all achievements and notifications."""
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.unlock_time = None
        self.notifications = []

    def draw_notifications(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Render active achievement notifications."""
        current_time = time.time()
        active: List[Dict[str, Any]] = []
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

    def draw_menu(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        """Render the achievements menu surface."""
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

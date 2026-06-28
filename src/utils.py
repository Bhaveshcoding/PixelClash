import pygame
import math
import random

def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamps a numeric scalar tightly between minimum and maximum bounds."""
    return max(min_val, min(value, max_val))

def lerp(start: float, end: float, alpha: float) -> float:
    """Linearly interpolates between two numeric points using a fractional alpha factor."""
    return start + (end - start) * alpha

def get_angle_to(origin: pygame.Vector2, target: pygame.Vector2) -> float:
    """Computes the exact directional angular heading in degrees from origin to target."""
    return math.degrees(math.atan2(target.y - origin.y, target.x - origin.x))

def calculate_screen_shake(timer: float, intensity: float) -> tuple[int, int]:
    """Generates random offset coordinates if an active screen shake timer is ticking."""
    if timer > 0.0:
        offset_x = random.randint(-int(intensity), int(intensity))
        offset_y = random.randint(-int(intensity), int(intensity))
        return offset_x, offset_y
    return 0, 0

def draw_text(surface: pygame.Surface, text: str, font: pygame.font.Font, color: tuple, position: tuple, center: bool = False):
    """Abstract blitting helper to output clean font text rendering passes."""
    text_surf = font.render(text, True, color)
    rect = text_surf.get_rect()
    if center:
        rect.center = position
    else:
        rect.topleft = position
    surface.blit(text_surf, rect)

def draw_health_bar(surface: pygame.Surface, x: int, y: int, width: int, height: int, current: float, max_val: float, bg_color=(200, 30, 30), fg_color=(30, 200, 30)):
    """Renders a structured health bar at specified world position targets."""
    pct = clamp(current / max_val if max_val > 0 else 0, 0.0, 1.0)
    pygame.draw.rect(surface, bg_color, (x, y, width, height))
    pygame.draw.rect(surface, fg_color, (x, y, int(width * pct), height))

import pygame
import os


class AssetManager:
    def __init__(self):
        self.images = {}
        self.sounds = {}
        self.fonts = {}

        self.image_path = "assets/images"
        self.sound_path = "assets/sounds"
        self.font_path = "assets/fonts"

        self.images["player_blue"] = self.generate_player(
            (0,180,255),
            (30,30,30)
        )

        self.images["player_red"] = self.generate_player(
            (255,80,80),
            (60,10,10)
        )

    def generate_player(self, body_color, gun_color):

        surf = pygame.Surface((40, 40), pygame.SRCALPHA)

        pygame.draw.rect(
            surf,
            body_color,
            (0, 0, 40, 40),
            border_radius=6
        )

        pygame.draw.rect(
            surf,
            gun_color,
            (28, 16, 12, 8)
        )

        return surf
    ###################################################
    # IMAGES
    ###################################################

    def get_image(self, name):
        if name in self.images:
            return self.images[name]

        filename = os.path.join(self.image_path, name + ".png")

        try:
            img = pygame.image.load(filename).convert_alpha()
        except Exception:
            img = pygame.Surface((40, 40), pygame.SRCALPHA)
            img.fill((255, 0, 255))

        self.images[name] = img
        return img

    ###################################################
    # SOUNDS
    ###################################################

    def get_sound(self, name):
        if name in self.sounds:
            return self.sounds[name]

        filename = os.path.join(self.sound_path, name + ".wav")

        try:
            snd = pygame.mixer.Sound(filename)
        except Exception:
            snd = None

        self.sounds[name] = snd
        return snd

    ###################################################
    # FONTS
    ###################################################

    def get_font(self, size, name="Arial", bold=False):

        key = (name, size, bold)

        if key in self.fonts:
            return self.fonts[key]

        font = pygame.font.SysFont(name, size, bold)

        self.fonts[key] = font

        return font
assets = AssetManager()
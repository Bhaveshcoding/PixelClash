import json
import os


class ProfileManager:
    def __init__(self, path="profile.json"):
        self.path = path
        self.data = {
            "player_name": "Player",
            "crosshair": "default",
            "fullscreen": False,
            "music_volume": 0.5,
            "sfx_volume": 0.5,
            "show_fps": True,
            "total_matches": 0,
            "total_wins": 0,
            "favorite_weapon": "Pistol",
            "favorite_skin": "default",
            "last_played": "",
        }
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            self.data.update(loaded)
        else:
            self.save()
        return self.data

    def save(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=4)
        return self.data

    def update_match(self, winner=False, weapon=None):
        self.data["total_matches"] += 1
        if winner:
            self.data["total_wins"] += 1
        if weapon:
            self.data["favorite_weapon"] = weapon
        self.data["last_played"] = "now"
        self.save()

    def update_settings(self, **kwargs):
        for key, value in kwargs.items():
            if key in self.data:
                self.data[key] = value
        self.save()

    def reset(self):
        self.data = {
            "player_name": "Player",
            "crosshair": "default",
            "fullscreen": False,
            "music_volume": 0.5,
            "sfx_volume": 0.5,
            "show_fps": True,
            "total_matches": 0,
            "total_wins": 0,
            "favorite_weapon": "Pistol",
            "favorite_skin": "default",
            "last_played": "",
        }
        self.save()

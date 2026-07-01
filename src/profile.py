import json
import os
from typing import Any, Dict, Optional


class ProfileManager:
    """Persist and update player profile settings and match history."""

    def __init__(self, path: str = "profile.json") -> None:
        self.path = path
        self.data: Dict[str, Any] = {
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

    def load(self) -> Dict[str, Any]:
        """Load profile data from disk, creating it if missing."""
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            self.data.update(loaded)
        else:
            self.save()
        return self.data

    def save(self) -> Dict[str, Any]:
        """Write the current profile data to disk."""
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=4)
        return self.data

    def update_match(self, winner: bool = False, weapon: Optional[int] = None) -> None:
        """Update profile stats after a match completes."""
        self.data["total_matches"] += 1
        if winner:
            self.data["total_wins"] += 1
        if weapon is not None:
            self.data["favorite_weapon"] = weapon
        self.data["last_played"] = "now"
        self.save()

    def update_settings(self, **kwargs: Any) -> None:
        """Apply a set of settings updates to the profile."""
        for key, value in kwargs.items():
            if key in self.data:
                self.data[key] = value
        self.save()

    def reset(self) -> None:
        """Reset the profile back to its default values."""
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

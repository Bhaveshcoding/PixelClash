import json
import os
from typing import Any, Dict, Optional


class ConfigManager:
    """Load and save lightweight game configuration values."""

    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or os.path.join(os.path.dirname(__file__), "config.json")
        self.defaults: Dict[str, Any] = {
            "player_speed": 400,
            "dash_cooldown": 1.5,
            "respawn_time": 3.0,
            "kill_limit": 10,
            "music_volume": 0.5,
            "sfx_volume": 0.5,
            "weapon_damage": 20,
            "weapon_fire_rate": 0.25,
            "grenade_damage": 60,
            "grenade_radius": 150,
            "particle_amount": 8,
            "camera_shake_strength": 6,
        }
        self.data: Dict[str, Any] = {}
        self.load()

    def load(self) -> Dict[str, Any]:
        """Load config from disk, creating it if missing."""
        if not os.path.exists(self.path):
            self.save()

        with open(self.path, "r", encoding="utf-8") as handle:
            self.data = json.load(handle)

        for key, default_value in self.defaults.items():
            self.data.setdefault(key, default_value)

        self.save()
        return self.data

    def save(self) -> Dict[str, Any]:
        """Persist the current config values to disk."""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(self.data, handle, indent=4)
        return self.data

    def get(self, key: str, default: Any = None) -> Any:
        """Return a config value, falling back to a default when present."""
        if key in self.data:
            return self.data[key]
        if default is not None:
            return default
        return self.defaults.get(key)

    def set(self, key: str, value: Any) -> Dict[str, Any]:
        """Set a config value and persist it immediately."""
        self.data[key] = value
        self.save()
        return self.data

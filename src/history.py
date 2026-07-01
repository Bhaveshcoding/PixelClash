import json
import os
from datetime import datetime
from typing import Any, Dict, List


class HistoryManager:
    """Persist and summarize previous match results."""

    def __init__(self, folder: str = "matches") -> None:
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    def save_match(self, winner: str, duration: float, player_stats: Dict[str, Any]) -> str:
        """Save a match result to disk and return the written file path."""
        files = [name for name in os.listdir(self.folder) if name.endswith(".json")]
        next_index = len(files) + 1
        filename = os.path.join(self.folder, f"match_{next_index:03d}.json")
        payload = {
            "winner": winner,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "duration": duration,
            "players": player_stats,
        }
        with open(filename, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=4)
        self.cleanup()
        return filename

    def load_matches(self) -> List[Dict[str, Any]]:
        """Load all saved matches sorted by newest first."""
        matches: List[Dict[str, Any]] = []
        for filename in sorted(os.listdir(self.folder)):
            if filename.endswith(".json"):
                path = os.path.join(self.folder, filename)
                with open(path, "r", encoding="utf-8") as handle:
                    matches.append(json.load(handle))
        return sorted(matches, key=lambda item: item.get("date", ""), reverse=True)

    def get_career_stats(self) -> Dict[str, Any]:
        """Return aggregate career statistics from stored matches."""
        matches = self.load_matches()
        if not matches:
            return {
                "matches_played": 0,
                "wins": 0,
                "losses": 0,
                "overall_accuracy": 0.0,
                "average_damage": 0.0,
                "average_survival_time": 0.0,
                "highest_kill_streak": 0,
                "average_kills": 0.0,
                "average_deaths": 0.0,
            }

        total_accuracy = 0.0
        total_damage = 0.0
        total_survival = 0.0
        total_kills = 0.0
        total_deaths = 0.0
        wins = 0
        highest = 0
        for match in matches:
            players = match.get("players", {})
            for stats in players.values():
                total_accuracy += stats.get("accuracy", 0)
                total_damage += stats.get("damage_dealt", 0)
                total_survival += stats.get("time_alive", 0)
                total_kills += stats.get("kills", 0)
                total_deaths += stats.get("deaths", 0)
            if match.get("winner"):
                wins += 1
            highest = max(highest, max((player.get("longest_kill_streak", 0) for player in players.values()), default=0))

        player_count = max(1, len(matches) * len(matches[0].get("players", {})))
        return {
            "matches_played": len(matches),
            "wins": wins,
            "losses": len(matches) - wins,
            "overall_accuracy": round(total_accuracy / player_count, 2),
            "average_damage": round(total_damage / player_count, 2),
            "average_survival_time": round(total_survival / player_count, 2),
            "highest_kill_streak": highest,
            "average_kills": round(total_kills / player_count, 2),
            "average_deaths": round(total_deaths / player_count, 2),
        }

    def cleanup(self) -> None:
        """Prune old history files to keep the folder bounded."""
        files = sorted(os.path.join(self.folder, name) for name in os.listdir(self.folder) if name.endswith(".json"))
        for extra in files[:-100]:
            if os.path.exists(extra):
                os.remove(extra)

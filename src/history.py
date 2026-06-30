import json
import os
from datetime import datetime


class HistoryManager:
    def __init__(self, folder="matches"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    def save_match(self, winner, duration, player_stats):
        files = [f for f in os.listdir(self.folder) if f.endswith(".json")]
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

    def load_matches(self):
        matches = []
        for filename in sorted(os.listdir(self.folder)):
            if filename.endswith(".json"):
                path = os.path.join(self.folder, filename)
                with open(path, "r", encoding="utf-8") as handle:
                    data = json.load(handle)
                matches.append(data)
        return sorted(matches, key=lambda item: item.get("date", ""), reverse=True)

    def get_career_stats(self):
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
            highest = max(highest, max((p.get("longest_kill_streak", 0) for p in players.values()), default=0))
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

    def cleanup(self):
        files = sorted([os.path.join(self.folder, f) for f in os.listdir(self.folder) if f.endswith(".json")])
        for extra in files[:-100]:
            if os.path.exists(extra):
                os.remove(extra)

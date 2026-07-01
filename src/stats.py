from typing import Dict, Union


class PlayerStats:
    """Container for per-player combat statistics."""

    def __init__(self) -> None:
        self.kills = 0
        self.deaths = 0
        self.shots_fired = 0
        self.shots_hit = 0
        self.grenades_thrown = 0
        self.grenade_hits = 0
        self.damage_dealt = 0
        self.damage_taken = 0
        self.pickups_collected = 0
        self.crates_destroyed = 0
        self.current_kill_streak = 0
        self.longest_kill_streak = 0
        self.time_alive = 0.0
        self.accuracy = 0.0

    def reset(self) -> None:
        """Reset the tracked values to their defaults."""
        self.__init__()


class StatsManager:
    """Manage combat statistics for players."""

    def __init__(self) -> None:
        self.players: Dict[Union[int, str], PlayerStats] = {}

    def get_player(self, pid: Union[int, str]) -> PlayerStats:
        """Return the stats object for a player, creating it if needed."""
        player = self.players.get(pid)
        if player is None:
            player = PlayerStats()
            self.players[pid] = player
        return player

    def record_shot(self, pid: Union[int, str]) -> None:
        self.get_player(pid).shots_fired += 1

    def record_hit(self, pid: Union[int, str], damage: int) -> None:
        player = self.get_player(pid)
        player.shots_hit += 1
        player.damage_dealt += damage

    def record_damage_taken(self, pid: Union[int, str], damage: int) -> None:
        self.get_player(pid).damage_taken += damage

    def record_grenade_hit(self, pid: Union[int, str]) -> None:
        self.get_player(pid).grenade_hits += 1

    def record_grenade(self, pid: Union[int, str]) -> None:
        self.get_player(pid).grenades_thrown += 1

    def record_pickup(self, pid: Union[int, str]) -> None:
        self.get_player(pid).pickups_collected += 1

    def record_crate(self, pid: Union[int, str]) -> None:
        self.get_player(pid).crates_destroyed += 1

    def record_kill(self, pid: Union[int, str]) -> None:
        player = self.get_player(pid)
        player.kills += 1
        player.current_kill_streak += 1
        if player.current_kill_streak > player.longest_kill_streak:
            player.longest_kill_streak = player.current_kill_streak

    def record_death(self, pid: Union[int, str]) -> None:
        player = self.get_player(pid)
        player.deaths += 1
        player.current_kill_streak = 0

    def update_alive(self, pid: Union[int, str], dt: float) -> None:
        self.get_player(pid).time_alive += dt

    def calculate_accuracy(self, pid: Union[int, str]) -> None:
        player = self.get_player(pid)
        player.accuracy = 0.0 if player.shots_fired == 0 else (player.shots_hit / player.shots_fired) * 100

    def reset_all(self) -> None:
        for player in self.players.values():
            player.reset()

    def get_stats(self, pid: Union[int, str]) -> PlayerStats:
        return self.get_player(pid)            
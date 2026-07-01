import copy
from collections import deque
from typing import Any, Deque, Dict, List, Optional


class ReplayManager:
    """Store and replay recent gameplay frames for the replay feature."""

    def __init__(self) -> None:
        self.frames: Deque[Dict[str, Any]] = deque(maxlen=1800)
        self.playing = False
        self.frame_index = 0

    def record(
        self,
        players: Dict[str, Any],
        bullets: List[Any],
        grenades: List[Any],
        pickups: Dict[str, Any],
        crates: List[Any],
        kill_feed: List[str],
        winner: str,
    ) -> None:
        """Append a deep-copied frame to the replay buffer."""
        frame = {
            "players": copy.deepcopy(players),
            "bullets": copy.deepcopy(bullets),
            "grenades": copy.deepcopy(grenades),
            "pickups": copy.deepcopy(pickups),
            "crates": copy.deepcopy(crates),
            "kill_feed": copy.deepcopy(kill_feed),
            "winner": winner,
        }
        self.frames.append(frame)

    def start(self) -> None:
        """Begin replay playback from the latest available frame."""
        if not self.frames:
            return
        self.playing = True
        self.frame_index = max(0, len(self.frames) - 1800)

    def stop(self) -> None:
        """Stop replay playback."""
        self.playing = False
        self.frame_index = 0

    def next_frame(self) -> Optional[Dict[str, Any]]:
        """Return the next replay frame or None when playback finishes."""
        if self.frame_index >= len(self.frames):
            self.stop()
            return None

        frame = self.frames[self.frame_index]
        self.frame_index += 1
        return frame
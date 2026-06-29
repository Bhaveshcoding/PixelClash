from collections import deque
import copy


class ReplayManager:

    def __init__(self):

        self.frames = deque(maxlen=1800)

        self.playing = False

        self.frame_index = max(
            0,
            len(self.frames) - 1800
        )
    
    def record(
        self,
        players,
        bullets,
        grenades,
        pickups,
        crates,
        kill_feed,
        winner
    ):

        frame = {

            "players": copy.deepcopy(players),

            "bullets": copy.deepcopy(bullets),

            "grenades": copy.deepcopy(grenades),

            "pickups": copy.deepcopy(pickups),

            "crates": copy.deepcopy(crates),

            "kill_feed": copy.deepcopy(kill_feed),

            "winner": winner

        }

        self.frames.append(frame)

    def start(self):

        if not self.frames:
            return

        self.playing = True

        self.frame_index = max(
            0,
            len(self.frames) - 1800
        )
    def stop(self):

        self.playing = False

        self.frame_index = 0

    def next_frame(self):

        if self.frame_index >= len(self.frames):

            self.stop()

            return None

        frame = self.frames[self.frame_index]

        self.frame_index += 1

        return frame
class PlayerStats:
    def __init__(self):
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

        self.time_alive = 0

        self.accuracy = 0
        
    def reset(self):
        self.__init__()

class StatsManager:

    def __init__(self):

        self.players = {}
    def get_player(self,pid):
        if pid not in self.players:

            self.players[pid]=PlayerStats()

        return self.players[pid]
    def record_shot(self,pid):
        self.get_player(pid).shots_fired+=1
        
    def record_hit(self,pid,damage):

        p=self.get_player(pid)

        p.shots_hit+=1

        p.damage_dealt+=damage
    def record_damage_taken(self,pid,damage):

        self.get_player(pid).damage_taken+=damage
    def record_grenade_hit(self,pid):

        self.get_player(pid).grenade_hits+=1
    def record_grenade(self, pid):

        self.get_player(pid).grenades_thrown += 1
    def record_pickup(self,pid):

        self.get_player(pid).pickups_collected+=1
    def record_crate(self,pid):

        self.get_player(pid).crates_destroyed+=1
        
    def record_kill(self,pid):

        p=self.get_player(pid)

        p.kills+=1

        p.current_kill_streak+=1

        if p.current_kill_streak>p.longest_kill_streak:

            p.longest_kill_streak=p.current_kill_streak
    def record_death(self,pid):

        p=self.get_player(pid)

        p.deaths+=1

        p.current_kill_streak=0
    def update_alive(self,pid,dt):
        self.get_player(pid).time_alive+=dt

    def calculate_accuracy(self,pid):
        p=self.get_player(pid)

        if p.shots_fired==0:

            p.accuracy=0

        else:

            p.accuracy=(

                p.shots_hit

                /

                p.shots_fired

            )*100
    def reset_all(self):
        for p in self.players.values():

            p.reset()
            
    def get_stats(self, pid):
        return self.get_player(pid)
            
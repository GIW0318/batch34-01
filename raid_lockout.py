class RaidLockout:
    def __init__(self, durations, period=604800):
        pass

    def enter(self, player, raid_id, difficulty, now):
        return None

    def available(self, player, raid_id, difficulty, now):
        return None

    def remaining(self, player, raid_id, difficulty, now):
        return None

    def reset(self, player=None):
        return None

    def state(self):
        return {}

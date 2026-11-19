class Leaderboard:
    def __init__(self, season=1):
        self.season = season
        self.entries = {}

    def submit(self, player, score, now):
        return None

    def top(self, n):
        return []

    def reset(self, season, now):
        return None

    def state(self):
        return {}

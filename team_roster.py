class TeamRoster:
    def __init__(self, max_size=5, role_limits=None):
        self.max_size = max_size
        self.role_limits = role_limits or {"tank": 1, "healer": 1, "dps": 3}
        self.members = {}

    def add(self, player, role, rating):
        return None

    def remove(self, player):
        return None

    def swap(self, player, role):
        return None

    def average_rating(self):
        return None

    def ready(self):
        return None

    def state(self):
        return {}

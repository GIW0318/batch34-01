class ReplayBookmarks:
    def __init__(self, retention=100):
        pass

    def add(self, marker_id, replay_id, player, ts, label, now, duration=None):
        return None

    def remove(self, marker_id, player):
        return None

    def share(self, marker_id, owner, target):
        return None

    def visible(self, replay_id, player):
        return []

    def prune(self, now):
        return []

    def state(self):
        return {}

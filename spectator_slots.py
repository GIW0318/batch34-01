class SpectatorSlots:
    def __init__(self, capacity=2, delay=5):
        pass

    def open_match(self, match_id, host):
        return None

    def join(self, match_id, viewer, now):
        return None

    def leave(self, match_id, viewer):
        return None

    def set_role(self, match_id, actor, viewer, role):
        return None

    def visible(self, match_id, viewer, event_ts, now):
        return None

    def kick(self, match_id, actor, viewer):
        return None

    def state(self):
        return {}

class SpectatorHub:
    ROLES = ("viewer", "referee", "admin")

    def __init__(self, slots=4, delay=90):
        self.slots = slots
        self.delay = delay
        self.matches = {}
        self.banned = set()

    def open_match(self, match_id, now):
        if now < 0:
            raise ValueError("match start time cannot be negative")
        if match_id in self.matches:
            raise ValueError("match already exists")
        self.matches[match_id] = {"start": now, "viewers": {}}
        return match_id

    def join(self, match_id, viewer, role="viewer", now=0):
        match = self.matches.get(match_id)
        if match is None:
            raise ValueError("unknown match")
        if role not in self.ROLES:
            raise ValueError("unknown role")
        if viewer in self.banned:
            raise ValueError("account is banned")
        if viewer in match["viewers"]:
            raise ValueError("viewer already joined")
        if now < match["start"]:
            raise ValueError("match has not started")
        if role == "viewer" and self._viewer_count(match) >= self.slots:
            raise ValueError("spectator slots are full")
        match["viewers"][viewer] = role
        return viewer

    def leave(self, match_id, viewer):
        match = self.matches.get(match_id)
        if match is not None:
            match["viewers"].pop(viewer, None)
        return viewer

    def visible_time(self, match_id, viewer, now):
        match = self.matches.get(match_id)
        if match is None or viewer not in match["viewers"]:
            raise ValueError("viewer has not joined the match")
        if match["viewers"][viewer] == "viewer":
            return max(now - self.delay, 0)
        return now

    def kick(self, match_id, actor, target):
        match = self.matches.get(match_id)
        if match is None:
            raise ValueError("unknown match")
        if match["viewers"].get(actor) != "admin":
            raise ValueError("only an admin in the room can kick")
        if actor == target:
            raise ValueError("admin cannot kick itself")
        if target not in match["viewers"]:
            raise ValueError("target is not in the room")
        del match["viewers"][target]
        self.banned.add(target)
        return target

    def state(self):
        return {"matches": self.matches, "banned": self.banned}

    def _viewer_count(self, match):
        return sum(1 for role in match["viewers"].values() if role == "viewer")

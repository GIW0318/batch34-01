class MovementValidator:
    def __init__(self, speed=10.0, tolerance=1.2, max_violations=3):
        self.speed = speed
        self.tolerance = tolerance
        self.max_violations = max_violations
        self.players = {}

    def move(self, player, x, y, now):
        return None

    def teleport(self, player, x, y, now):
        return None

    def position(self, player):
        return None

    def violations(self, player):
        return 0

    def state(self):
        return {}

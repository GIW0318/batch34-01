class EnergyPool:
    def __init__(self, cap=100, regen_seconds=60):
        self.cap = cap
        self.regen_seconds = regen_seconds
        self.value = cap
        self.last = 0
        self.progress = 0

    def spend(self, amount, now):
        return None

    def current(self, now):
        return None

    def state(self):
        return {}

class GuildBank:
    def __init__(self, roles):
        self.roles = roles
        self.balance = 0
        self.audit = []

    def deposit(self, role, amount):
        return None

    def withdraw(self, role, amount, ref=None):
        return None

    def set_limit(self, role, limit):
        return None

    def state(self):
        return {}

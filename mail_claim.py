class MailBox:
    def __init__(self, capacity=20, ttl=30):
        self.capacity = capacity
        self.ttl = ttl
        self.mails = {}
        self.players = set()

    def send(self, mail_id, recipient, attachments, now):
        return None

    def claim(self, mail_id, now):
        return None

    def expire(self, now):
        return []

    def state(self):
        return {}

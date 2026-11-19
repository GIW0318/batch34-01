import copy

DAY_SECONDS = 86400


class GiftManager:
    def __init__(self, daily_limit=5, ttl=3600):
        self.daily_limit = daily_limit
        self.ttl = ttl
        self._friends = {}
        self._gifts = []

    @staticmethod
    def _valid_name(name):
        return isinstance(name, str) and name.strip() != ""

    @staticmethod
    def _day_of(timestamp):
        return timestamp // DAY_SECONDS

    def add_friend(self, a, b):
        if not self._valid_name(a) or not self._valid_name(b):
            raise ValueError("friend name must not be blank")
        if a == b:
            raise ValueError("cannot add yourself as a friend")
        self._friends.setdefault(a, set()).add(b)
        self._friends.setdefault(b, set()).add(a)

    def _are_friends(self, a, b):
        return b in self._friends.get(a, set())

    def _used_today(self, sender, day):
        return sum(
            gift["count"]
            for gift in self._gifts
            if gift["sender"] == sender and self._day_of(gift["sent_at"]) == day
        )

    def send(self, sender, receiver, gift_id, now, count=1):
        if not self._are_friends(sender, receiver):
            raise ValueError("sender and receiver are not friends")
        if count <= 0:
            raise ValueError("gift count must be positive")

        day = self._day_of(now)
        for gift in self._gifts:
            if (
                gift["sender"] == sender
                and gift["gift_id"] == gift_id
                and self._day_of(gift["sent_at"]) == day
            ):
                raise ValueError("gift_id already sent today")

        if self._used_today(sender, day) + count > self.daily_limit:
            raise ValueError("daily gift limit exceeded")

        record = {
            "gift_id": gift_id,
            "sender": sender,
            "receiver": receiver,
            "count": count,
            "sent_at": now,
            "expires": now + self.ttl,
            "claimed": False,
        }
        self._gifts.append(record)
        return copy.deepcopy(record)

    def _has_reciprocal_gift(self, receiver, sender, day):
        return any(
            gift["sender"] == receiver
            and gift["receiver"] == sender
            and self._day_of(gift["sent_at"]) == day
            for gift in self._gifts
        )

    def claim(self, receiver, sender, gift_id, now):
        matches = [
            gift
            for gift in self._gifts
            if gift["sender"] == sender
            and gift["receiver"] == receiver
            and gift["gift_id"] == gift_id
        ]
        if not matches:
            raise ValueError("gift not found")

        if not self._has_reciprocal_gift(receiver, sender, self._day_of(now)):
            raise ValueError("receiver has not sent a reciprocal gift today")

        for gift in matches:
            if not gift["claimed"] and now < gift["expires"]:
                gift["claimed"] = True
                return copy.deepcopy(gift)

        if any(gift["claimed"] for gift in matches):
            raise ValueError("gift already claimed")
        raise ValueError("gift has expired")

    def pending(self, receiver, now):
        return sorted(
            {
                gift["gift_id"]
                for gift in self._gifts
                if gift["receiver"] == receiver
                and not gift["claimed"]
                and now < gift["expires"]
            }
        )

    def state(self):
        return {"gifts": copy.deepcopy(self._gifts)}

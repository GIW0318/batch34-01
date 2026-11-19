from copy import deepcopy


class TradeMail:
    def __init__(self, wallets=None):
        self._wallets = deepcopy(wallets) if wallets is not None else {}
        self._mails = {}

    def send(self, mail_id, sender, recipient, item, price, now, ttl):
        if mail_id in self._mails:
            raise ValueError("duplicate mail id")
        if not self._valid_item(item):
            raise ValueError("item must be a non-empty mapping of positive quantities")
        if not self._valid_number(price) or price < 0:
            raise ValueError("price must be non-negative")
        if not self._valid_number(ttl) or ttl <= 0:
            raise ValueError("ttl must be positive")
        if sender not in self._wallets:
            raise ValueError("unknown sender")
        if recipient not in self._wallets:
            raise ValueError("unknown recipient")

        sender_wallet = self._wallets[sender]
        items = sender_wallet.setdefault("items", {})
        for name, quantity in item.items():
            if items.get(name, 0) < quantity:
                raise ValueError("sender does not own enough of the item")

        for name, quantity in item.items():
            items[name] -= quantity
            if items[name] == 0:
                del items[name]

        mail = {
            "id": mail_id,
            "sender": sender,
            "recipient": recipient,
            "item": deepcopy(item),
            "price": price,
            "sent_at": now,
            "ttl": ttl,
            "expires_at": now + ttl,
            "status": "pending",
        }
        self._mails[mail_id] = mail
        return deepcopy(mail)

    def claim(self, mail_id, player, now):
        mail = self._mails.get(mail_id)
        if mail is None:
            raise ValueError("unknown mail id")
        if player != mail["recipient"]:
            raise PermissionError("only the recipient can claim this mail")
        if mail["status"] != "pending":
            raise ValueError("mail is not pending")
        if now >= mail["expires_at"]:
            raise ValueError("mail has expired")

        wallet = self._wallets[player]
        price = mail["price"]
        if wallet.get("gold", 0) < price:
            raise ValueError("insufficient gold")

        if price:
            wallet["gold"] -= price
            sender_wallet = self._wallets[mail["sender"]]
            sender_wallet["gold"] = sender_wallet.get("gold", 0) + price

        recipient_items = wallet.setdefault("items", {})
        for name, quantity in mail["item"].items():
            recipient_items[name] = recipient_items.get(name, 0) + quantity

        mail["status"] = "claimed"
        mail["claimed_at"] = now
        return deepcopy(mail)

    def expire(self, now):
        expired = []
        for mail_id, mail in self._mails.items():
            if mail["status"] != "pending" or now < mail["expires_at"]:
                continue

            sender_items = self._wallets[mail["sender"]].setdefault("items", {})
            for name, quantity in mail["item"].items():
                sender_items[name] = sender_items.get(name, 0) + quantity

            mail["status"] = "expired"
            mail["expired_at"] = now
            expired.append(mail_id)
        return expired

    def inbox(self, player):
        return [
            mail_id
            for mail_id, mail in self._mails.items()
            if mail["recipient"] == player and mail["status"] == "pending"
        ]

    def state(self):
        return {
            "mails": deepcopy(self._mails),
            "wallets": deepcopy(self._wallets),
        }

    @staticmethod
    def _valid_number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool)

    @staticmethod
    def _valid_item(item):
        return (
            isinstance(item, dict)
            and bool(item)
            and all(
                TradeMail._valid_number(quantity) and quantity > 0
                for quantity in item.values()
            )
        )

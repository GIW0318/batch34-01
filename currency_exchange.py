class CurrencyExchange:
    def __init__(
        self,
        wallets=None,
        fee_rate=0.02,
        min_amount=10,
        max_amount=1000,
        daily_limit=2000,
        rate_ttl=60,
    ):
        self._wallets = {
            player: dict(balances) for player, balances in (wallets or {}).items()
        }
        self._fee_rate = fee_rate
        self._min_amount = min_amount
        self._max_amount = max_amount
        self._daily_limit = daily_limit
        self._rate_ttl = rate_ttl
        self._rates = {}
        self._daily_used = {}
        self._requests = {}

    def set_rate(self, base, quote, rate, now):
        if base == quote:
            raise ValueError("base and quote currency must differ")
        if rate <= 0:
            raise ValueError("rate must be positive")
        self._rates[(base, quote)] = (float(rate), now)
        return None

    def _get_rate(self, base, quote, now):
        if base == quote:
            raise ValueError("base and quote currency must differ")
        direct = self._rates.get((base, quote))
        if direct is not None:
            rate, ts = direct
            if now - ts <= self._rate_ttl:
                return rate
        inverse = self._rates.get((quote, base))
        if inverse is not None:
            rate, ts = inverse
            if now - ts <= self._rate_ttl:
                return 1.0 / rate
        raise ValueError("no fresh rate for pair")

    def quote(self, amount, base, quote, now):
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount < self._min_amount or amount > self._max_amount:
            raise ValueError("amount out of allowed range")
        rate = self._get_rate(base, quote, now)
        converted = amount * rate
        fee = round(converted * self._fee_rate, 2)
        credited = round(converted - fee, 2)
        return {
            "amount": amount,
            "base": base,
            "quote": quote,
            "rate": rate,
            "fee": fee,
            "credited": credited,
        }

    def convert(self, player, amount, base, quote, now, request_id=None):
        if request_id is not None and request_id in self._requests:
            return dict(self._requests[request_id])
        result = self.quote(amount, base, quote, now)
        wallet = self._wallets.get(player)
        if wallet is None or wallet.get(base, 0) < amount:
            raise ValueError("insufficient balance")
        day = int(now // 86400)
        used = self._daily_used.get((player, day), 0.0)
        if used + amount > self._daily_limit:
            raise ValueError("daily limit exceeded")
        wallet[base] = wallet.get(base, 0) - amount
        wallet[quote] = wallet.get(quote, 0) + result["credited"]
        self._daily_used[(player, day)] = used + amount
        if request_id is not None:
            self._requests[request_id] = dict(result)
        return result

    def used_today(self, player, now):
        day = int(now // 86400)
        return self._daily_used.get((player, day), 0.0)

    def state(self):
        return {
            "wallets": {
                player: dict(balances)
                for player, balances in self._wallets.items()
            }
        }

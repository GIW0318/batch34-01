class ServerTransfer:
    def __init__(self, servers, weights=None, bound=None, max_weight=50, cooldown=100):
        self.servers = {
            name: {"capacity": data["capacity"], "players": list(data["players"])}
            for name, data in servers.items()
        }
        self.weights = dict(weights or {})
        self.bound = set(bound or set())
        self.max_weight = max_weight
        self.cooldown = cooldown
        self.transfers = {}
        self.inventories = {}
        self.cooldowns = {}

    def request(self, transfer_id, player, source, target, inventory, now):
        if transfer_id in self.transfers:
            raise ValueError("duplicate transfer id")
        if source not in self.servers:
            raise ValueError("unknown source server")
        if target not in self.servers:
            raise ValueError("unknown target server")
        if source == target:
            raise ValueError("source and target must differ")
        if player not in self.servers[source]["players"]:
            raise ValueError("player is not on the source server")
        last_commit = self.cooldowns.get(player)
        if last_commit is not None and now - last_commit < self.cooldown:
            raise ValueError("transfer cooldown is still active")
        if len(self.servers[target]["players"]) >= self.servers[target]["capacity"]:
            raise ValueError("target server is full")
        total_weight = 0
        for item, count in inventory.items():
            if item in self.bound:
                raise ValueError("bound items cannot be transferred")
            total_weight += self.weights.get(item, 0) * count
        if total_weight > self.max_weight:
            raise ValueError("inventory is overweight")
        self.transfers[transfer_id] = {
            "player": player,
            "source": source,
            "target": target,
            "inventory": dict(inventory),
            "status": "pending",
        }

    def commit(self, transfer_id, player, now):
        transfer = self.transfers.get(transfer_id)
        if transfer is None:
            raise ValueError("unknown transfer")
        if transfer["player"] != player:
            raise ValueError("transfer does not belong to this player")
        if transfer["status"] != "pending":
            raise ValueError("transfer is not pending")
        source = transfer["source"]
        target = transfer["target"]
        if player not in self.servers[source]["players"]:
            raise ValueError("player is not on the source server")
        if len(self.servers[target]["players"]) >= self.servers[target]["capacity"]:
            raise ValueError("target server is full")
        self.servers[source]["players"].remove(player)
        self.servers[target]["players"].append(player)
        self.inventories[player] = dict(transfer["inventory"])
        self.cooldowns[player] = now
        transfer["status"] = "committed"

    def cancel(self, transfer_id, player, now):
        transfer = self.transfers.get(transfer_id)
        if transfer is None:
            raise ValueError("unknown transfer")
        if transfer["player"] != player:
            raise ValueError("transfer does not belong to this player")
        if transfer["status"] != "pending":
            raise ValueError("transfer is not pending")
        transfer["status"] = "cancelled"

    def state(self):
        return {
            "servers": {
                name: {"capacity": data["capacity"], "players": list(data["players"])}
                for name, data in self.servers.items()
            },
            "transfers": {
                transfer_id: dict(transfer)
                for transfer_id, transfer in self.transfers.items()
            },
            "inventories": {
                player: dict(inventory)
                for player, inventory in self.inventories.items()
            },
        }

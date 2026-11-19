class GuildWar:
    def __init__(self, nodes, lock_seconds=100):
        self.nodes = {node_id: dict(data) for node_id, data in nodes.items()}
        self.lock_seconds = lock_seconds
        self.owners = {}
        self.locks = {}
        self._scores = {}
        self.settled = False

    def attack(self, guild, node_id, power, now):
        if self.settled:
            raise ValueError("guild war has already been settled")
        if node_id is None or node_id == "" or node_id not in self.nodes:
            raise ValueError("unknown node")
        if type(power) is not int or power <= 0:
            raise ValueError("power must be a positive integer")

        owner = self.owners.get(node_id)
        if owner is not None and owner == guild:
            raise ValueError("cannot attack a node owned by your guild")
        if owner is not None and now < self.locks[node_id]:
            raise ValueError("node is locked")

        node = self.nodes[node_id]
        if power < node["defense"]:
            raise ValueError("power is below node defense")

        if owner is not None:
            self._scores[owner] = self._scores.get(owner, 0) - node["value"]
        self.owners[node_id] = guild
        self._scores[guild] = self._scores.get(guild, 0) + node["value"]
        self.locks[node_id] = now + self.lock_seconds

    def score(self, guild):
        return self._scores.get(guild, 0)

    def settle(self):
        if self.settled:
            raise ValueError("guild war has already been settled")
        self.settled = True

    def state(self):
        return {
            "owners": dict(self.owners),
            "locks": dict(self.locks),
            "scores": dict(self._scores),
            "settled": self.settled,
        }

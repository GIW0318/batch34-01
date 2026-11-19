class CraftingQueue:
    def __init__(self, recipes, inventory, capacity=3):
        self.recipes = recipes
        self.inventory = inventory
        self.capacity = capacity
        self.jobs = {}
        self._job_index = {}
        self.clock = 0

    def enqueue(self, player, job_id, recipe_id, qty, now):
        if recipe_id not in self.recipes:
            raise ValueError("unknown recipe: %r" % (recipe_id,))
        if isinstance(qty, bool) or not isinstance(qty, int) or qty < 1:
            raise ValueError("invalid quantity: %r" % (qty,))
        if job_id is None or job_id == "":
            raise ValueError("invalid job id: %r" % (job_id,))
        if job_id in self._job_index:
            raise ValueError("duplicate job id: %r" % (job_id,))

        queue = self.jobs.setdefault(player, [])
        active = [job for job in queue if job["status"] == "queued"]
        if len(active) >= self.capacity:
            raise ValueError("queue is full for player %r" % (player,))

        recipe = self.recipes[recipe_id]
        materials = recipe.get("materials", {})
        for item, amount in materials.items():
            if self.inventory.get(item, 0) < amount * qty:
                raise ValueError("insufficient material: %r" % (item,))

        self.clock = max(self.clock, now)
        for item, amount in materials.items():
            self.inventory[item] = self.inventory.get(item, 0) - amount * qty

        start = now
        for job in active:
            start = max(start, job["end"])
        end = start + recipe.get("duration", 0) * qty

        job = {
            "player": player,
            "job_id": job_id,
            "recipe": recipe_id,
            "qty": qty,
            "status": "queued",
            "start": start,
            "end": end,
        }
        queue.append(job)
        self._job_index[job_id] = job
        return job

    def tick(self, now):
        if now < self.clock:
            raise ValueError("tick time cannot go backwards")
        self.clock = now
        for player in self.jobs:
            for job in self.jobs[player]:
                if job["status"] == "queued" and job["end"] <= now:
                    recipe = self.recipes[job["recipe"]]
                    for item, amount in recipe.get("output", {}).items():
                        self.inventory[item] = (
                            self.inventory.get(item, 0) + amount * job["qty"]
                        )
                    job["status"] = "completed"
        return None

    def cancel(self, player, job_id, now):
        job = self._job_index.get(job_id)
        if job is None or job["player"] != player:
            raise ValueError("unknown job: %r" % (job_id,))
        self.clock = max(self.clock, now)
        if job["status"] != "queued" or job["start"] <= self.clock:
            raise ValueError("job %r cannot be cancelled" % (job_id,))
        recipe = self.recipes[job["recipe"]]
        for item, amount in recipe.get("materials", {}).items():
            self.inventory[item] = (
                self.inventory.get(item, 0) + amount * job["qty"]
            )
        job["status"] = "cancelled"
        return None

    def status(self, player):
        return [
            {
                "job_id": job["job_id"],
                "recipe": job["recipe"],
                "recipe_id": job["recipe"],
                "qty": job["qty"],
                "status": job["status"],
                "start": job["start"],
                "end": job["end"],
            }
            for job in self.jobs.get(player, [])
        ]

    def state(self):
        return {
            "inventory": dict(self.inventory),
            "capacity": self.capacity,
            "clock": self.clock,
            "players": {player: self.status(player) for player in self.jobs},
        }

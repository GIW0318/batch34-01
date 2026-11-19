import math


class WorldBoss:
    def __init__(self, max_hp, phases, reward_pool=1000):
        if not isinstance(max_hp, int) or isinstance(max_hp, bool) or max_hp <= 0:
            raise ValueError("max_hp must be a positive integer")
        if (
            not isinstance(reward_pool, (int, float))
            or isinstance(reward_pool, bool)
            or not math.isfinite(reward_pool)
            or reward_pool < 0
        ):
            raise ValueError("reward_pool must be a non-negative number")

        self.phases = self._validate_phases(phases)
        self.max_hp = max_hp
        self.reward_pool = reward_pool
        self.hp = max_hp
        self.phase = 0
        self.contributions = {}
        self.settled = False
        self._rewards = {}

    @staticmethod
    def _validate_phases(phases):
        if not isinstance(phases, (list, tuple)) or not phases:
            raise ValueError("phases must be a non-empty list")

        validated = []
        previous_threshold = None
        for phase in phases:
            if not isinstance(phase, dict):
                raise ValueError("each phase must be a mapping")

            threshold = phase.get("threshold")
            multiplier = phase.get("multiplier")
            if (
                not isinstance(threshold, (int, float))
                or isinstance(threshold, bool)
                or not math.isfinite(threshold)
                or threshold <= 0
                or threshold > 1
            ):
                raise ValueError("phase threshold must be in (0, 1]")
            if (
                not isinstance(multiplier, (int, float))
                or isinstance(multiplier, bool)
                or not math.isfinite(multiplier)
                or multiplier <= 0
            ):
                raise ValueError("phase multiplier must be a positive number")
            if previous_threshold is not None and threshold >= previous_threshold:
                raise ValueError("phase thresholds must be strictly decreasing")

            validated.append(
                {"threshold": threshold, "multiplier": multiplier}
            )
            previous_threshold = threshold

        return validated

    def _phase_for_hp(self):
        ratio = self.hp / self.max_hp
        phase = 0
        for index, config in enumerate(self.phases):
            if ratio <= config["threshold"]:
                phase = index
        return phase

    def attack(self, player, damage, now):
        if self.settled or self.hp <= 0:
            raise ValueError("cannot attack a defeated or settled boss")
        if (
            not isinstance(damage, int)
            or isinstance(damage, bool)
            or damage <= 0
        ):
            raise ValueError("damage must be a positive integer")

        multiplier = self.phases[self.phase]["multiplier"]
        effective_damage = min(damage * multiplier, self.hp)
        self.hp -= effective_damage
        self.contributions[player] = (
            self.contributions.get(player, 0) + effective_damage
        )
        self.phase = max(self.phase, self._phase_for_hp())
        return effective_damage

    def settle(self):
        if self.settled:
            raise ValueError("this battle has already been settled")
        if self.hp > 0:
            raise ValueError("cannot settle before the boss is defeated")

        total_contribution = sum(self.contributions.values())
        rewards = {}
        if total_contribution:
            for player, contribution in self.contributions.items():
                rewards[player] = int(
                    self.reward_pool * contribution // total_contribution
                )

        self.reward_pool -= sum(rewards.values())
        self._rewards = rewards
        self.settled = True
        return dict(rewards)

    def reward(self, player):
        if not self.settled:
            raise ValueError("rewards are not available before settlement")
        if player not in self.contributions:
            raise ValueError("player has no contribution record")
        return self._rewards[player]

    def state(self):
        return {
            "hp": self.hp,
            "phase": self.phase,
            "alive": self.hp > 0,
            "contributions": dict(self.contributions),
            "settled": self.settled,
        }

import copy


class QuestChain:
    def __init__(self, quests):
        if not isinstance(quests, dict):
            raise ValueError("quests must be a mapping")

        self._quests = copy.deepcopy(quests)
        self._choice_targets = set()

        for quest_id, quest in self._quests.items():
            if not isinstance(quest, dict):
                raise ValueError("invalid quest definition: %s" % quest_id)

            branches = quest.get("branches", {})
            if not isinstance(branches, dict):
                raise ValueError("invalid branches for quest: %s" % quest_id)

            for target in branches.values():
                if target not in self._quests:
                    raise ValueError("unknown branch target: %s" % target)
                self._choice_targets.add(target)

        self._players = {}

    def register(self, player):
        if player in self._players:
            raise ValueError("player already registered: %s" % player)

        self._players[player] = {
            "flags": [],
            "gold": 0,
            "quests": {},
            "choices": {},
            "locked_out": [],
        }

    def available(self, player):
        player_state = self._player_state(player)
        return [
            quest_id
            for quest_id in self._quests
            if self._quest_status(player_state, quest_id) == "available"
        ]

    def accept(self, player, quest_id):
        player_state = self._player_state(player)
        self._require_quest(quest_id)

        if self._quest_status(player_state, quest_id) != "available":
            raise ValueError("quest is not available: %s" % quest_id)

        player_state["quests"][quest_id] = "active"

    def complete(self, player, quest_id):
        player_state = self._player_state(player)
        quest = self._require_quest(quest_id)

        if player_state["quests"].get(quest_id) != "active":
            raise ValueError("quest is not active: %s" % quest_id)

        before = set(self.available(player))

        player_state["quests"][quest_id] = "completed"
        for flag in quest.get("grants", []):
            if flag not in player_state["flags"]:
                player_state["flags"].append(flag)
        player_state["gold"] += quest.get("coins", 0)

        after = set(self.available(player))
        return [
            other_id
            for other_id in self._quests
            if other_id in after and other_id not in before
        ]

    def choose(self, player, quest_id, option):
        player_state = self._player_state(player)
        quest = self._require_quest(quest_id)
        branches = quest.get("branches", {})

        if option not in branches:
            raise ValueError("unknown branch option: %s" % option)
        if player_state["quests"].get(quest_id) != "completed":
            raise ValueError("quest must be completed before choosing: %s" % quest_id)
        if quest_id in player_state["choices"]:
            raise ValueError("branch already chosen for quest: %s" % quest_id)

        target = branches[option]
        player_state["choices"][quest_id] = option

        for branch_target in branches.values():
            if branch_target != target and branch_target not in player_state["locked_out"]:
                player_state["locked_out"].append(branch_target)

    def status(self, player, quest_id):
        player_state = self._player_state(player)
        self._require_quest(quest_id)
        return self._quest_status(player_state, quest_id)

    def flags(self, player):
        return list(self._player_state(player)["flags"])

    def gold(self, player):
        return self._player_state(player)["gold"]

    def state(self):
        return copy.deepcopy({"players": self._players})

    def _player_state(self, player):
        try:
            return self._players[player]
        except KeyError:
            raise ValueError("unknown player: %s" % player)

    def _require_quest(self, quest_id):
        try:
            return self._quests[quest_id]
        except KeyError:
            raise ValueError("unknown quest: %s" % quest_id)

    def _quest_status(self, player_state, quest_id):
        quest_state = player_state["quests"].get(quest_id)
        if quest_state == "completed":
            return "completed"
        if quest_state == "active":
            return "active"
        if quest_id in player_state["locked_out"]:
            return "locked_out"

        if quest_id in self._choice_targets:
            selected = any(
                self._quests[parent_id]["branches"][option] == quest_id
                for parent_id, option in player_state["choices"].items()
            )
            if not selected:
                return "locked"

        if self._requirements_met(player_state, quest_id):
            return "available"
        return "locked"

    def _requirements_met(self, player_state, quest_id):
        required = self._quests[quest_id].get("requires", [])
        flags = set(player_state["flags"])
        return all(flag in flags for flag in required)

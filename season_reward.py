class SeasonReward:
    def __init__(self, brackets, season_end, claim_grace=0):
        pass

    def reward_for(self, rank):
        return None

    def settle(self, player, rank, now):
        return None

    def claim(self, player, now):
        return None

    def expired_unclaimed(self, now):
        return None

    def state(self):
        return {}

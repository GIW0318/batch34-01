import pytest

import season_reward as sr

BRACKETS = [(1, 1, 1000), (2, 10, 500), (11, 100, 100)]
END = 10_000
GRACE = 500


def shell():
    return sr.SeasonReward(list(BRACKETS), season_end=END, claim_grace=GRACE)


def test_top_rank_reward_payload():
    s = shell()
    assert s.reward_for(1) == {"coins": 1000, "low": 1, "high": 1}


def test_bracket_edges_map_to_expected_rewards():
    s = shell()
    assert s.reward_for(2)["coins"] == 500
    assert s.reward_for(10)["coins"] == 500
    assert s.reward_for(11)["coins"] == 100
    assert s.reward_for(100)["coins"] == 100


def test_rank_beyond_last_bracket_is_rejected():
    s = shell()
    with pytest.raises(ValueError):
        s.reward_for(101)


def test_rank_zero_is_rejected():
    s = shell()
    with pytest.raises(ValueError):
        s.reward_for(0)


def test_settle_stores_rank_and_coins():
    s = shell()
    s.settle("alice", 7, now=9000)
    out = s.state()["players"]["alice"]
    assert out["rank"] == 7
    assert out["coins"] == 500
    assert out["claimed"] is False


def test_settle_after_season_end_is_rejected():
    s = shell()
    with pytest.raises(ValueError):
        s.settle("alice", 3, now=END + 1)


def test_settling_twice_is_rejected():
    s = shell()
    s.settle("alice", 3, now=9000)
    with pytest.raises(ValueError):
        s.settle("alice", 4, now=9100)


def test_claim_before_settle_is_rejected():
    s = shell()
    with pytest.raises(ValueError):
        s.claim("alice", now=9000)


def test_claim_returns_recorded_reward():
    s = shell()
    s.settle("alice", 25, now=9000)
    assert s.claim("alice", now=9500) == {"rank": 25, "coins": 100}


def test_claiming_twice_is_rejected():
    s = shell()
    s.settle("alice", 4, now=9000)
    s.claim("alice", now=9500)
    with pytest.raises(ValueError):
        s.claim("alice", now=9600)


def test_claim_after_deadline_is_rejected():
    s = shell()
    s.settle("alice", 2, now=9000)
    with pytest.raises(ValueError):
        s.claim("alice", now=END + GRACE + 1)


def test_claim_at_deadline_is_allowed():
    s = shell()
    s.settle("alice", 2, now=9000)
    assert s.claim("alice", now=END + GRACE) == {"rank": 2, "coins": 500}


def test_expired_unclaimed_lists_settled_players():
    s = shell()
    s.settle("alice", 2, now=9000)
    s.settle("bob", 60, now=9500)
    s.claim("bob", now=9700)
    assert s.expired_unclaimed(now=END + GRACE) == []
    assert s.expired_unclaimed(now=END + GRACE + 1) == ["alice"]


def test_state_is_a_detached_snapshot():
    s = shell()
    s.settle("alice", 2, now=9000)
    snap = s.state()
    snap["players"]["alice"]["coins"] = 1
    assert s.claim("alice", now=9500)["coins"] == 500


def test_brackets_must_start_at_rank_one():
    with pytest.raises(ValueError):
        sr.SeasonReward([(2, 5, 10)], season_end=END, claim_grace=GRACE)
    with pytest.raises(ValueError):
        sr.SeasonReward([(1, 5, 10), (5, 9, 20)], season_end=END, claim_grace=GRACE)

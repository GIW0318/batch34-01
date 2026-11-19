import pytest

import achievement_chain as ac

DEFS = {
    "novice": {"event": "kill", "need": 3, "prereq": [], "reward": 50, "points": 5},
    "slayer": {"event": "kill", "need": 5, "prereq": [], "reward": 90, "points": 8},
    "veteran": {"event": "boss", "need": 2, "prereq": ["novice"], "reward": 120, "points": 20},
}


def chain():
    c = ac.AchievementChain(DEFS)
    c.register("alice")
    return c


def test_record_below_threshold_returns_empty():
    c = chain()
    assert c.record("alice", "kill", 2) == []
    p = c.progress("alice")
    assert p["novice"]["have"] == 2
    assert p["novice"]["need"] == 3
    assert p["novice"]["state"] == "locked"


def test_reaching_threshold_unlocks_only_once():
    c = chain()
    assert c.record("alice", "kill", 3) == ["novice"]
    assert c.record("alice", "kill", 1) == []
    assert c.pending("alice") == ["novice"]


def test_one_record_can_unlock_several_in_definition_order():
    c = chain()
    assert c.record("alice", "kill", 5) == ["novice", "slayer"]
    assert c.pending("alice") == ["novice", "slayer"]


def test_unclaimed_prereq_blocks_later_unlock():
    c = chain()
    assert c.record("alice", "boss", 2) == []
    assert c.progress("alice")["veteran"]["have"] == 2
    c.record("alice", "kill", 3)
    c.claim("alice", "novice")
    assert c.record("alice", "boss", 1) == ["veteran"]


def test_claim_pays_reward_exactly_once():
    c = chain()
    c.record("alice", "kill", 3)
    assert c.claim("alice", "novice") == {"gold": 50}
    assert c.balance("alice") == 50
    assert c.points("alice") == 5
    with pytest.raises(ValueError):
        c.claim("alice", "novice")
    assert c.balance("alice") == 50
    assert c.points("alice") == 5


def test_claim_before_unlock_is_rejected():
    c = chain()
    with pytest.raises(ValueError):
        c.claim("alice", "novice")


def test_claim_of_unknown_achievement_is_rejected():
    c = chain()
    c.record("alice", "kill", 3)
    with pytest.raises(ValueError):
        c.claim("alice", "phantom")


def test_pending_skips_claimed_in_definition_order():
    c = chain()
    c.record("alice", "kill", 5)
    assert c.pending("alice") == ["novice", "slayer"]
    c.claim("alice", "slayer")
    assert c.pending("alice") == ["novice"]


def test_progress_reports_each_state():
    c = chain()
    c.record("alice", "kill", 3)
    c.claim("alice", "novice")
    p = c.progress("alice")
    assert p["novice"]["state"] == "claimed"
    assert p["slayer"]["state"] == "locked"
    assert p["veteran"]["state"] == "locked"
    assert p["veteran"]["have"] == 0


def test_unknown_event_is_ignored():
    c = chain()
    assert c.record("alice", "dance", 9) == []
    assert c.progress("alice")["novice"]["have"] == 0
    assert c.balance("alice") == 0


def test_unregistered_player_cannot_record():
    c = ac.AchievementChain(DEFS)
    with pytest.raises(ValueError):
        c.record("bob", "kill", 1)


def test_duplicate_register_is_rejected():
    c = ac.AchievementChain(DEFS)
    c.register("alice")
    with pytest.raises(ValueError):
        c.register("alice")


def test_non_positive_count_is_rejected():
    c = chain()
    with pytest.raises(ValueError):
        c.record("alice", "kill", 0)
    with pytest.raises(ValueError):
        c.record("alice", "kill", -3)


def test_state_is_a_deep_copy():
    c = chain()
    c.record("alice", "kill", 3)
    s = c.state()
    s["players"]["alice"]["gold"] = 9999
    s["players"]["alice"]["counters"]["kill"] = 99
    assert c.balance("alice") == 0
    assert c.progress("alice")["novice"]["have"] == 3


def test_unknown_player_lookup_is_rejected():
    c = chain()
    with pytest.raises(ValueError):
        c.balance("nobody")

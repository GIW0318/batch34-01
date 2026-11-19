import pytest

import battle_pass as bpm

THRESHOLDS = [100, 300, 600, 1000]


def fresh():
    return bpm.BattlePass(list(THRESHOLDS), season="s1")


def test_new_member_starts_at_tier_zero():
    b = fresh()
    b.join("alice")
    assert b.tier("alice") == 0
    assert b.state()["players"]["alice"]["xp"] == 0


def test_add_xp_raises_tier_at_threshold():
    b = fresh()
    b.join("alice")
    assert b.add_xp("alice", 99) == 0
    assert b.add_xp("alice", 1) == 1
    assert b.add_xp("alice", 200) == 2


def test_xp_is_capped_at_top_threshold():
    b = fresh()
    b.join("alice")
    b.add_xp("alice", 5000)
    assert b.tier("alice") == 4
    assert b.state()["players"]["alice"]["xp"] == 1000


def test_joining_twice_is_rejected():
    b = fresh()
    b.join("alice")
    with pytest.raises(ValueError):
        b.join("alice")


def test_blank_member_name_is_rejected():
    b = fresh()
    with pytest.raises(ValueError):
        b.join("   ")


def test_add_xp_for_unknown_member_is_rejected():
    b = fresh()
    with pytest.raises(ValueError):
        b.add_xp("ghost", 10)


def test_add_xp_rejects_zero_and_negative():
    b = fresh()
    b.join("alice")
    with pytest.raises(ValueError):
        b.add_xp("alice", 0)
    with pytest.raises(ValueError):
        b.add_xp("alice", -5)
    assert b.tier("alice") == 0


def test_claim_before_unlock_is_rejected():
    b = fresh()
    b.join("alice")
    b.add_xp("alice", 99)
    with pytest.raises(ValueError):
        b.claim("alice", 1)


def test_claim_returns_reward_payload():
    b = fresh()
    b.join("alice")
    b.add_xp("alice", 300)
    assert b.claim("alice", 2) == {"tier": 2, "coins": 100}


def test_claiming_same_tier_twice_is_rejected():
    b = fresh()
    b.join("alice")
    b.add_xp("alice", 300)
    b.claim("alice", 1)
    with pytest.raises(ValueError):
        b.claim("alice", 1)


def test_claim_outside_known_tiers_is_rejected():
    b = fresh()
    b.join("alice")
    b.add_xp("alice", 1000)
    with pytest.raises(ValueError):
        b.claim("alice", 0)
    with pytest.raises(ValueError):
        b.claim("alice", 5)


def test_claimed_tiers_are_recorded_in_order():
    b = fresh()
    b.join("alice")
    b.add_xp("alice", 600)
    b.claim("alice", 3)
    b.claim("alice", 1)
    assert b.state()["players"]["alice"]["claimed"] == [1, 3]


def test_state_is_detached_from_internal_progress():
    b = fresh()
    b.join("alice")
    b.add_xp("alice", 300)
    snap = b.state()
    snap["players"]["alice"]["xp"] = 0
    snap["players"]["alice"]["claimed"].append(9)
    assert b.tier("alice") == 2
    assert b.state()["players"]["alice"]["claimed"] == []


def test_reset_season_archives_progress_and_clears():
    b = fresh()
    b.join("alice")
    b.add_xp("alice", 600)
    b.claim("alice", 1)
    b.reset_season("s2")
    assert b.current_season() == "s2"
    s = b.state()
    assert s["players"]["alice"]["xp"] == 0
    assert s["players"]["alice"]["claimed"] == []
    archived = s["archives"]["s1"]["players"]["alice"]
    assert archived["xp"] == 600
    assert archived["tier"] == 3
    assert archived["claimed"] == [1]


def test_reset_season_rejects_repeated_name():
    b = fresh()
    with pytest.raises(ValueError):
        b.reset_season("s1")
    with pytest.raises(ValueError):
        b.reset_season("")

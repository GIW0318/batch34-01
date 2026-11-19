import pytest

import loot_pity as lp


def pity(**kw):
    cfg = {"hard_pity": 10, "soft_pity": 8, "base_rate": 0.05, "guarantee": True}
    cfg.update(kw)
    p = lp.LootPity(**cfg)
    p.register("alice")
    return p


def pump(p, n, roll=0.99, flip=0.5):
    out = None
    for _ in range(n):
        out = p.draw("alice", roll, flip)
    return out


def test_high_roll_is_not_rare():
    p = pity()
    r = p.draw("alice", 0.99, 0.5)
    assert r["rare"] is False
    assert r["counter"] == 1
    assert r["pulls"] == 1
    assert r["guaranteed"] is False


def test_low_roll_is_rare_and_marks_guarantee():
    p = pity()
    r = p.draw("alice", 0.0, 0.9)
    assert r["rare"] is True
    assert r["featured"] is False
    assert r["guaranteed"] is True
    assert r["counter"] == 0


def test_low_flip_gives_featured():
    p = pity()
    r = p.draw("alice", 0.0, 0.1)
    assert r["featured"] is True
    assert r["guaranteed"] is False


def test_hard_pity_forces_rare():
    p = pity()
    pump(p, 9)
    r = p.draw("alice", 0.999, 0.5)
    assert r["rare"] is True
    assert r["counter"] == 0
    assert r["pulls"] == 10


def test_soft_pity_raises_rate():
    p = pity()
    pump(p, 7)
    r = p.draw("alice", 0.10, 0.5)
    assert r["rare"] is True


def test_base_rate_applies_before_soft_pity():
    p = pity()
    pump(p, 6, roll=0.06)
    r = p.draw("alice", 0.999, 0.5)
    assert r["rare"] is False
    assert r["counter"] == 7


def test_guarantee_forces_featured_next_rare():
    p = pity()
    p.draw("alice", 0.0, 0.9)
    r = p.draw("alice", 0.0, 0.9)
    assert r["rare"] is True
    assert r["featured"] is True
    assert r["guaranteed"] is False


def test_counter_resets_after_rare():
    p = pity()
    pump(p, 3)
    p.draw("alice", 0.0, 0.5)
    r = p.draw("alice", 0.99, 0.5)
    assert r["rare"] is False
    assert r["counter"] == 1


def test_pulls_counts_every_draw():
    p = pity()
    pump(p, 5, roll=0.5)
    r = p.draw("alice", 0.0, 0.5)
    assert r["pulls"] == 6


def test_state_is_a_deep_copy():
    p = pity()
    p.draw("alice", 0.99, 0.5)
    s = p.state()
    s["players"]["alice"]["counter"] = 77
    s["players"]["alice"]["pulls"] = 77
    assert p.state()["players"]["alice"]["counter"] == 1
    assert p.state()["players"]["alice"]["pulls"] == 1


def test_roll_out_of_range_rejected():
    p = pity()
    with pytest.raises(ValueError):
        p.draw("alice", 1.0, 0.5)
    with pytest.raises(ValueError):
        p.draw("alice", -0.1, 0.5)


def test_flip_out_of_range_rejected():
    p = pity()
    with pytest.raises(ValueError):
        p.draw("alice", 0.5, 1.0)


def test_unregistered_player_rejected():
    p = lp.LootPity()
    with pytest.raises(ValueError):
        p.draw("bob", 0.5, 0.5)


def test_duplicate_register_rejected():
    p = lp.LootPity()
    p.register("alice")
    with pytest.raises(ValueError):
        p.register("alice")


def test_constructor_rejects_soft_pity_not_below_hard():
    with pytest.raises(ValueError):
        lp.LootPity(hard_pity=10, soft_pity=10)

import pytest

import energy_regen as er


def pool(cap=10, sec=10):
    return er.EnergyPool(cap, sec)


def test_starts_full():
    assert pool().current(0) == 10


def test_spend_reduces_value():
    game = pool()
    game.spend(3, 0)
    assert game.current(0) == 7


def test_regen_after_interval():
    game = pool()
    game.spend(3, 0)
    assert game.current(10) == 8


def test_regen_accumulates_offline():
    game = pool()
    game.spend(10, 0)
    assert game.current(50) == 5


def test_cap_stops_regen():
    game = pool()
    game.spend(1, 0)
    assert game.current(1000) == 10


def test_partial_progress_is_kept():
    game = pool()
    game.spend(1, 0)
    game.current(5)
    assert game.current(10) == 10


def test_spend_settles_first():
    game = pool()
    game.spend(5, 0)
    game.spend(1, 10)
    assert game.current(10) == 4


def test_negative_spend_raises():
    with pytest.raises(ValueError):
        pool().spend(-1, 0)


def test_zero_spend_raises():
    with pytest.raises(ValueError):
        pool().spend(0, 0)


def test_overspend_raises():
    with pytest.raises(ValueError):
        pool().spend(11, 0)


def test_non_integer_spend_raises():
    with pytest.raises(ValueError):
        pool().spend(1.5, 0)


def test_invalid_cap_raises():
    with pytest.raises(ValueError):
        er.EnergyPool(0, 10)


def test_invalid_interval_raises():
    with pytest.raises(ValueError):
        er.EnergyPool(10, 0)


def test_time_backwards_raises():
    game = pool()
    game.current(10)
    with pytest.raises(ValueError):
        game.current(9)


def test_state_returns_a_copy():
    game = pool()
    game.spend(2, 0)
    snapshot = game.state()
    snapshot["value"] = 99
    assert game.state()["value"] == 8

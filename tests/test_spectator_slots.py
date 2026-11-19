import pytest

import spectator_slots as sp


def arena(capacity=2, delay=5):
    return sp.SpectatorSlots(capacity=capacity, delay=delay)


def opened(capacity=2, delay=5):
    game = arena(capacity=capacity, delay=delay)
    game.open_match("m1", "host")
    return game


def test_open_match_registers_host():
    game = opened()
    match = game.state()["matches"]["m1"]
    assert match["host"] == "host"
    assert match["slots"] == {}


def test_duplicate_match_is_rejected():
    game = opened()
    with pytest.raises(ValueError):
        game.open_match("m1", "other")


def test_join_occupies_a_slot():
    game = opened()
    game.join("m1", "v1", 0)
    assert game.state()["matches"]["m1"]["slots"] == {"v1": "viewer"}


def test_capacity_is_enforced():
    game = opened(capacity=1)
    game.join("m1", "v1", 0)
    with pytest.raises(ValueError):
        game.join("m1", "v2", 1)


def test_rejoin_does_not_take_extra_slot():
    game = opened()
    game.join("m1", "v1", 0)
    game.join("m1", "v1", 1)
    assert game.state()["matches"]["m1"]["slots"] == {"v1": "viewer"}


def test_leave_frees_slot():
    game = opened(capacity=1)
    game.join("m1", "v1", 0)
    game.leave("m1", "v1")
    game.join("m1", "v2", 2)
    assert list(game.state()["matches"]["m1"]["slots"]) == ["v2"]


def test_unknown_match_is_rejected():
    game = arena()
    with pytest.raises(ValueError):
        game.join("missing", "v1", 0)


def test_viewer_sees_event_after_delay():
    game = opened(delay=5)
    game.join("m1", "v1", 0)
    assert game.visible("m1", "v1", 10, 14) is False
    assert game.visible("m1", "v1", 10, 15) is True


def test_viewer_cannot_see_future_event():
    game = opened(delay=5)
    game.join("m1", "v1", 0)
    assert game.visible("m1", "v1", 100, 12) is False


def test_referee_sees_event_without_delay():
    game = opened(delay=5)
    game.join("m1", "v1", 0)
    game.set_role("m1", "host", "v1", "referee")
    assert game.visible("m1", "v1", 10, 10) is True


def test_non_host_cannot_assign_role():
    game = opened()
    game.join("m1", "v1", 0)
    game.join("m1", "v2", 1)
    with pytest.raises(PermissionError):
        game.set_role("m1", "v1", "v2", "referee")


def test_host_can_promote_viewer():
    game = opened()
    game.join("m1", "v1", 0)
    game.set_role("m1", "host", "v1", "referee")
    assert game.state()["matches"]["m1"]["slots"]["v1"] == "referee"


def test_kicked_viewer_cannot_rejoin():
    game = opened()
    game.join("m1", "v1", 0)
    game.kick("m1", "host", "v1")
    with pytest.raises(PermissionError):
        game.join("m1", "v1", 5)


def test_non_host_cannot_kick():
    game = opened()
    game.join("m1", "v1", 0)
    game.join("m1", "v2", 1)
    with pytest.raises(PermissionError):
        game.kick("m1", "v1", "v2")
    assert "v2" in game.state()["matches"]["m1"]["slots"]


def test_state_returns_detached_copy():
    game = opened()
    game.join("m1", "v1", 0)
    snapshot = game.state()
    snapshot["matches"]["m1"]["slots"]["v1"] = "referee"
    assert game.state()["matches"]["m1"]["slots"]["v1"] == "viewer"

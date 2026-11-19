import pytest

import team_roster as tr


def roster(max_size=5, limits=None):
    return tr.TeamRoster(max_size, limits or {"tank": 1, "healer": 1, "dps": 3})


def test_add_member_is_visible():
    game = roster()
    game.add("alice", "tank", 1200)
    assert game.state()["members"]["alice"]["role"] == "tank"


def test_unknown_role_rejected():
    with pytest.raises(ValueError):
        roster().add("bob", "mage", 1000)


def test_duplicate_player_rejected():
    game = roster()
    game.add("alice", "tank", 1200)
    with pytest.raises(ValueError):
        game.add("alice", "dps", 1300)


def test_rating_out_of_range_rejected():
    with pytest.raises(ValueError):
        roster().add("bob", "dps", 0)


def test_rating_must_be_integer():
    with pytest.raises(ValueError):
        roster().add("bob", "dps", "1200")


def test_role_cap_enforced():
    game = roster()
    game.add("alice", "tank", 1200)
    with pytest.raises(ValueError):
        game.add("bob", "tank", 1300)


def test_party_capacity_enforced():
    game = roster(2, {"dps": 2})
    game.add("a", "dps", 1000)
    game.add("b", "dps", 1000)
    with pytest.raises(ValueError):
        game.add("c", "dps", 1000)


def test_average_rating():
    game = roster()
    game.add("alice", "tank", 1200)
    game.add("bob", "healer", 1500)
    assert game.average_rating() == 1350.0


def test_average_of_empty_party_rejected():
    with pytest.raises(ValueError):
        roster().average_rating()


def test_not_ready_when_incomplete():
    game = roster(3, {"tank": 1, "healer": 1, "dps": 1})
    game.add("alice", "tank", 1200)
    assert game.ready() is False


def test_ready_when_full_and_composed():
    game = roster(3, {"tank": 1, "healer": 1, "dps": 1})
    game.add("alice", "tank", 1200)
    game.add("bob", "healer", 1300)
    game.add("cara", "dps", 1400)
    assert game.ready() is True


def test_not_ready_without_healer():
    game = roster(3, {"tank": 1, "healer": 1, "dps": 2})
    game.add("alice", "tank", 1200)
    game.add("bob", "dps", 1300)
    game.add("cara", "dps", 1400)
    assert game.ready() is False


def test_remove_member():
    game = roster()
    game.add("alice", "tank", 1200)
    game.remove("alice")
    assert "alice" not in game.state()["members"]


def test_swap_role():
    game = roster()
    game.add("alice", "tank", 1200)
    game.swap("alice", "healer")
    assert game.state()["members"]["alice"]["role"] == "healer"


def test_state_returns_a_copy():
    game = roster()
    game.add("alice", "tank", 1200)
    snapshot = game.state()
    snapshot["members"]["alice"]["rating"] = 9999
    assert game.state()["members"]["alice"]["rating"] == 1200

import pytest

import leaderboard_ties as lb


def board():
    return lb.Leaderboard(1)


def test_submit_adds_entry():
    game = board()
    game.submit("alice", 10, 0)
    assert game.top(1)[0]["player"] == "alice"


def test_higher_score_replaces():
    game = board()
    game.submit("alice", 10, 0)
    game.submit("alice", 20, 1)
    assert game.top(1)[0]["score"] == 20


def test_lower_score_does_not_replace():
    game = board()
    game.submit("alice", 20, 0)
    game.submit("alice", 10, 1)
    assert game.top(1)[0]["score"] == 20


def test_ties_break_by_earlier_time():
    game = board()
    game.submit("bob", 10, 1)
    game.submit("alice", 10, 0)
    assert [x["player"] for x in game.top(2)] == ["alice", "bob"]


def test_ties_break_by_player_id():
    game = board()
    game.submit("bob", 10, 0)
    game.submit("alice", 10, 0)
    assert [x["player"] for x in game.top(2)] == ["alice", "bob"]


def test_top_n_limits():
    game = board()
    game.submit("a", 10, 0)
    game.submit("b", 20, 0)
    assert len(game.top(1)) == 1


def test_top_zero_raises():
    with pytest.raises(ValueError):
        board().top(0)


def test_top_negative_raises():
    with pytest.raises(ValueError):
        board().top(-1)


def test_top_beyond_size_raises():
    game = board()
    game.submit("a", 10, 0)
    with pytest.raises(ValueError):
        game.top(2)


def test_reset_clears_entries():
    game = board()
    game.submit("a", 10, 0)
    game.reset(2, 1)
    assert game.state()["season"] == 2
    assert game.top(1) == []


def test_reset_changes_season():
    game = board()
    game.reset(2, 1)
    assert game.state()["season"] == 2


def test_invalid_score_raises():
    with pytest.raises(ValueError):
        board().submit("a", "10", 0)


def test_negative_score_raises():
    with pytest.raises(ValueError):
        board().submit("a", -1, 0)


def test_state_returns_a_copy():
    game = board()
    game.submit("a", 10, 0)
    snapshot = game.state()
    snapshot["entries"]["a"]["score"] = 99
    assert game.state()["entries"]["a"]["score"] == 10


def test_top_is_sorted():
    game = board()
    game.submit("a", 10, 0)
    game.submit("b", 30, 0)
    game.submit("c", 20, 0)
    assert [x["player"] for x in game.top(3)] == ["b", "c", "a"]

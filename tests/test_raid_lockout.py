import pytest

import raid_lockout as rl

DUR = {"normal": 3600, "hard": 7200, "heroic": 0}
WEEK = 604800


def raid(period=WEEK):
    return rl.RaidLockout(dict(DUR), period=period)


def test_first_kill_returns_expiry_and_locks_player():
    r = raid()
    exp = r.enter("p1", "dragon", "normal", now=100)
    assert exp == 3700
    assert r.available("p1", "dragon", "normal", now=101) is False


def test_second_kill_during_lockout_is_rejected():
    r = raid()
    r.enter("p1", "dragon", "normal", now=100)
    with pytest.raises(ValueError):
        r.enter("p1", "dragon", "normal", now=200)


def test_lockout_lifts_at_expiry_timestamp():
    r = raid()
    r.enter("p1", "dragon", "normal", now=100)
    assert r.available("p1", "dragon", "normal", now=3699) is False
    assert r.available("p1", "dragon", "normal", now=3700) is True


def test_remaining_seconds_count_down():
    r = raid()
    r.enter("p1", "dragon", "normal", now=100)
    assert r.remaining("p1", "dragon", "normal", now=200) == 3500


def test_remaining_is_zero_when_available():
    r = raid()
    assert r.remaining("p1", "dragon", "normal", now=100) == 0


def test_difficulties_lock_independently():
    r = raid()
    r.enter("p1", "dragon", "normal", now=100)
    assert r.available("p1", "dragon", "hard", now=200) is True
    assert r.remaining("p1", "dragon", "hard", now=200) == 0


def test_unknown_difficulty_is_rejected():
    r = raid()
    with pytest.raises(ValueError):
        r.enter("p1", "dragon", "mythic", now=100)


def test_zero_second_difficulty_never_locks():
    r = raid()
    assert r.enter("p1", "dragon", "heroic", now=100) == 100
    assert r.available("p1", "dragon", "heroic", now=100) is True
    assert r.enter("p1", "dragon", "heroic", now=100) == 100


def test_kill_count_increases_after_lockout_ends():
    r = raid()
    r.enter("p1", "dragon", "normal", now=100)
    r.enter("p1", "dragon", "normal", now=4000)
    assert r.state()["records"]["p1"]["dragon"]["normal"]["kills"] == 2


def test_period_rollover_clears_stale_lockout():
    r = raid()
    r.enter("p1", "dragon", "normal", now=WEEK - 100)
    assert r.available("p1", "dragon", "normal", now=WEEK + 100) is True


def test_reset_player_clears_their_lockouts():
    r = raid()
    r.enter("p1", "dragon", "normal", now=100)
    r.reset("p1")
    assert r.available("p1", "dragon", "normal", now=200) is True


def test_reset_without_player_clears_everyone():
    r = raid()
    r.enter("p1", "dragon", "normal", now=100)
    r.enter("p2", "dragon", "hard", now=100)
    r.reset()
    assert r.available("p1", "dragon", "normal", now=200) is True
    assert r.available("p2", "dragon", "hard", now=200) is True


def test_reset_unknown_player_is_rejected():
    r = raid()
    with pytest.raises(ValueError):
        r.reset("ghost")


def test_state_is_a_detached_snapshot():
    r = raid()
    r.enter("p1", "dragon", "normal", now=100)
    snap = r.state()
    snap["records"]["p1"]["dragon"]["normal"]["kills"] = 99
    assert r.state()["records"]["p1"]["dragon"]["normal"]["kills"] == 1


def test_negative_timestamp_is_rejected():
    r = raid()
    with pytest.raises(ValueError):
        r.enter("p1", "dragon", "normal", now=-1)

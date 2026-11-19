import pytest

import anti_speedhack as av


def validator(speed=10.0, tolerance=1.2, max_violations=3):
    return av.MovementValidator(speed, tolerance, max_violations)


def test_invalid_speed_rejected():
    with pytest.raises(ValueError):
        av.MovementValidator(0, 1.2, 3)


def test_first_move_registers():
    game = validator()
    assert game.move("alice", 0, 0, 0) == (True, None)


def test_normal_move_accepted():
    game = validator()
    game.move("alice", 0, 0, 0)
    assert game.move("alice", 5, 0, 1) == (True, None)


def test_fast_move_rejected():
    game = validator()
    game.move("alice", 0, 0, 0)
    assert game.move("alice", 50, 0, 1) == (False, "too_fast")


def test_violation_count_increments():
    game = validator()
    game.move("alice", 0, 0, 0)
    game.move("alice", 50, 0, 1)
    assert game.violations("alice") == 1


def test_position_frozen_after_reject():
    game = validator()
    game.move("alice", 0, 0, 0)
    game.move("alice", 50, 0, 1)
    assert game.position("alice") == (0.0, 0.0)


def test_position_updates_on_accept():
    game = validator()
    game.move("alice", 0, 0, 0)
    game.move("alice", 5, 0, 1)
    assert game.position("alice") == (5.0, 0.0)


def test_diagonal_uses_euclidean_distance():
    game = validator(5.0, 1.0, 3)
    game.move("alice", 0, 0, 0)
    assert game.move("alice", 3, 4, 1) == (True, None)


def test_tolerance_permits_small_overshoot():
    game = validator(10.0, 1.2, 3)
    game.move("alice", 0, 0, 0)
    assert game.move("alice", 11, 0, 1) == (True, None)


def test_same_timestamp_rejected():
    game = validator()
    game.move("alice", 0, 0, 0)
    with pytest.raises(ValueError):
        game.move("alice", 1, 0, 0)


def test_time_backwards_rejected():
    game = validator()
    game.move("alice", 0, 0, 0)
    game.move("alice", 1, 0, 2)
    with pytest.raises(ValueError):
        game.move("alice", 2, 0, 1)


def test_teleport_updates_position():
    game = validator()
    game.move("alice", 0, 0, 0)
    game.teleport("alice", 100, 50, 1)
    assert game.position("alice") == (100.0, 50.0)


def test_teleport_does_not_add_violation():
    game = validator()
    game.move("alice", 0, 0, 0)
    game.teleport("alice", 100, 50, 1)
    assert game.violations("alice") == 0
    assert game.position("alice") == (100.0, 50.0)


def test_flag_after_repeated_violations():
    game = validator(10.0, 1.2, 2)
    game.move("alice", 0, 0, 0)
    game.move("alice", 50, 0, 1)
    game.move("alice", 100, 0, 2)
    assert game.state()["players"]["alice"]["flagged"] is True


def test_unknown_player_position_raises():
    with pytest.raises(ValueError):
        validator().position("ghost")

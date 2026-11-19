import pytest

import guild_bank as gb

ROLES = {
    "member": {"deposit": True, "withdraw": False, "limit": 0},
    "officer": {"deposit": True, "withdraw": True, "limit": 100},
}


def bank():
    return gb.GuildBank({k: dict(v) for k, v in ROLES.items()})


def test_deposit_increases_balance():
    game = bank()
    game.deposit("member", 50)
    assert game.state()["balance"] == 50


def test_no_deposit_permission_raises():
    game = bank()
    game.roles["member"]["deposit"] = False
    with pytest.raises(ValueError):
        game.deposit("member", 10)


def test_withdraw_decreases_balance():
    game = bank()
    game.deposit("member", 50)
    game.withdraw("officer", 20)
    assert game.state()["balance"] == 30


def test_no_withdraw_permission_raises():
    game = bank()
    game.deposit("member", 50)
    with pytest.raises(ValueError):
        game.withdraw("member", 10)


def test_limit_is_enforced():
    game = bank()
    game.deposit("member", 500)
    game.set_limit("officer", 50)
    with pytest.raises(ValueError):
        game.withdraw("officer", 60)


def test_negative_deposit_raises():
    with pytest.raises(ValueError):
        bank().deposit("member", -1)


def test_negative_withdraw_raises():
    with pytest.raises(ValueError):
        bank().withdraw("officer", -1)


def test_insufficient_balance_raises():
    game = bank()
    with pytest.raises(ValueError):
        game.withdraw("officer", 10)


def test_audit_records_deposit():
    game = bank()
    game.deposit("member", 10)
    assert game.state()["audit"][-1]["type"] == "deposit"


def test_audit_records_withdraw():
    game = bank()
    game.deposit("member", 10)
    game.withdraw("officer", 5)
    assert game.state()["audit"][-1]["type"] == "withdraw"


def test_unknown_role_raises():
    with pytest.raises(ValueError):
        bank().deposit("ghost", 1)


def test_set_limit_updates_role():
    game = bank()
    game.set_limit("officer", 77)
    assert game.roles["officer"]["limit"] == 77


def test_duplicate_withdraw_reference_is_rejected():
    game = bank()
    game.deposit("member", 100)
    game.withdraw("officer", 10, ref="r1")
    with pytest.raises(ValueError):
        game.withdraw("officer", 10, ref="r1")


def test_zero_amount_raises():
    with pytest.raises(ValueError):
        bank().deposit("member", 0)


def test_state_returns_a_copy():
    game = bank()
    game.deposit("member", 10)
    snapshot = game.state()
    snapshot["balance"] = 99
    assert game.state()["balance"] == 10

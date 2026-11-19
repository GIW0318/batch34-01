import pytest

import mail_claim as mc


def box():
    game = mc.MailBox(2, 10)
    game.players.add("alice")
    return game


def test_send_adds_mail():
    game = box()
    game.send("m1", "alice", ["gold"], 0)
    assert game.state()["mails"]["m1"]["claimed"] is False


def test_unknown_recipient_raises():
    with pytest.raises(ValueError):
        box().send("m1", "ghost", [], 0)


def test_duplicate_mail_id_raises():
    game = box()
    game.send("m1", "alice", ["gold"], 0)
    with pytest.raises(ValueError):
        game.send("m1", "alice", ["gem"], 0)


def test_capacity_is_enforced():
    game = box()
    game.send("m1", "alice", [], 0)
    game.send("m2", "alice", [], 0)
    with pytest.raises(ValueError):
        game.send("m3", "alice", [], 0)


def test_claim_returns_attachments():
    game = box()
    game.send("m1", "alice", ["gold"], 0)
    assert game.claim("m1", 1) == ["gold"]


def test_claim_twice_raises():
    game = box()
    game.send("m1", "alice", ["gold"], 0)
    game.claim("m1", 1)
    with pytest.raises(ValueError):
        game.claim("m1", 2)


def test_expired_mail_cannot_be_claimed():
    game = box()
    game.send("m1", "alice", ["gold"], 0)
    with pytest.raises(ValueError):
        game.claim("m1", 11)


def test_expire_marks_mail():
    game = box()
    game.send("m1", "alice", ["gold"], 0)
    game.expire(11)
    assert game.state()["mails"]["m1"]["status"] == "expired"


def test_expire_returns_expired_ids():
    game = box()
    game.send("m1", "alice", [], 0)
    assert game.expire(11) == ["m1"]


def test_empty_attachment_is_allowed():
    game = box()
    game.send("m1", "alice", [], 0)
    assert game.claim("m1", 1) == []


def test_invalid_time_raises():
    game = box()
    with pytest.raises(ValueError):
        game.send("m1", "alice", [], -1)


def test_non_list_attachments_raises():
    game = box()
    with pytest.raises(ValueError):
        game.send("m1", "alice", "gold", 0)


def test_capacity_frees_after_expire():
    game = box()
    game.send("m1", "alice", [], 0)
    game.send("m2", "alice", [], 0)
    game.expire(11)
    game.send("m3", "alice", [], 11)
    assert "m3" in game.state()["mails"]


def test_state_returns_a_copy():
    game = box()
    game.send("m1", "alice", ["gold"], 0)
    snapshot = game.state()
    snapshot["mails"]["m1"]["claimed"] = True
    assert game.state()["mails"]["m1"]["claimed"] is False


def test_claim_unknown_mail_raises():
    with pytest.raises(ValueError):
        box().claim("ghost", 1)

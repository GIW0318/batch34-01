import pytest

import replay_bookmark as rb


def bookmarks(retention=100):
    return rb.ReplayBookmarks(retention=retention)


def test_add_marker_for_owner():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0, duration=60)
    items = game.visible("r1", "alice")
    assert len(items) == 1
    assert items[0]["ts"] == 10
    assert items[0]["label"] == "开团"
    assert items[0]["owner"] == "alice"


def test_duplicate_marker_id_is_rejected():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0)
    with pytest.raises(ValueError):
        game.add("k1", "r1", "bob", 20, "第二条", 1)


def test_negative_timestamp_is_rejected():
    game = bookmarks()
    with pytest.raises(ValueError):
        game.add("k1", "r1", "alice", -1, "坏点", 0)


def test_timestamp_beyond_duration_is_rejected():
    game = bookmarks()
    with pytest.raises(ValueError):
        game.add("k1", "r1", "alice", 61, "超界", 0, duration=60)


def test_empty_label_is_rejected():
    game = bookmarks()
    with pytest.raises(ValueError):
        game.add("k1", "r1", "alice", 10, "", 0)


def test_same_player_same_timestamp_is_rejected():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "一波", 0)
    with pytest.raises(ValueError):
        game.add("k2", "r1", "alice", 10, "重复", 1)


def test_non_owner_cannot_remove():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0)
    with pytest.raises(PermissionError):
        game.remove("k1", "bob")


def test_owner_can_remove_marker():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0)
    game.remove("k1", "alice")
    assert game.visible("r1", "alice") == []
    assert "k1" not in game.state()["markers"]


def test_shared_marker_visible_to_target():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0)
    game.share("k1", "alice", "bob")
    items = game.visible("r1", "bob")
    assert len(items) == 1
    assert items[0]["owner"] == "alice"


def test_unshared_marker_hidden_from_others():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0)
    assert game.visible("r1", "bob") == []
    assert len(game.visible("r1", "alice")) == 1


def test_share_twice_does_not_duplicate():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0)
    game.share("k1", "alice", "bob")
    game.share("k1", "alice", "bob")
    assert len(game.visible("r1", "bob")) == 1


def test_share_with_self_is_rejected():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0)
    with pytest.raises(ValueError):
        game.share("k1", "alice", "alice")


def test_prune_removes_expired_markers():
    game = bookmarks(retention=100)
    game.add("k1", "r1", "alice", 10, "旧标记", 0)
    removed = game.prune(101)
    assert removed == ["k1"]
    assert game.visible("r1", "alice") == []


def test_prune_keeps_marker_at_boundary():
    game = bookmarks(retention=100)
    game.add("k1", "r1", "alice", 10, "边界", 0)
    assert game.prune(100) == []
    assert len(game.visible("r1", "alice")) == 1


def test_state_returns_detached_copy():
    game = bookmarks()
    game.add("k1", "r1", "alice", 10, "开团", 0)
    snapshot = game.state()
    snapshot["markers"]["k1"]["label"] = "改坏了"
    assert game.visible("r1", "alice")[0]["label"] == "开团"

import pytest

import shop_rotation as sr

POOL = ["item-%02d" % i for i in range(50)]


def rot(slots=5, seed=7, tz=0):
    return sr.ShopRotation(POOL, slots, seed, tz_offset_minutes=tz)


def test_same_day_rotation_is_stable():
    r = rot()
    first = r.rotation_for(7)
    assert len(first) == 5
    assert first == r.rotation_for(7)


def test_different_seeds_produce_different_rotations():
    a = rot(seed=1).rotation_for(3)
    b = rot(seed=2).rotation_for(3)
    assert len(a) == 5
    assert a != b


def test_slots_control_rotation_length():
    assert len(rot(slots=4).rotation_for(0)) == 4
    assert len(rot(slots=9).rotation_for(0)) == 9


def test_rotation_has_no_duplicates():
    items = rot().rotation_for(11)
    assert len(items) == 5
    assert len(set(items)) == 5


def test_two_instances_agree():
    a = sr.ShopRotation(POOL, 5, 42).rotation_for(0)
    b = sr.ShopRotation(POOL, 5, 42).rotation_for(0)
    assert len(a) == 5
    assert a == b


def test_timezone_shifts_day_index():
    east = rot(tz=120)
    assert east.day_index(86399) == 1
    assert east.day_index(86399 - 7200) == 0
    assert rot(tz=0).day_index(86399) == 0


def test_negative_timestamp_floors_down():
    r = rot()
    assert r.day_index(-1) == -1
    assert r.day_index(-86400) == -1
    assert r.day_index(-86401) == -2


def test_rotation_at_follows_day_index():
    r = rot()
    assert len(r.rotation_for(5)) == 5
    assert r.rotation_at(5 * 86400 + 100) == r.rotation_for(5)


def test_remaining_seconds_to_local_midnight():
    r = rot()
    assert r.remaining_seconds(0) == 86400
    assert r.remaining_seconds(43200) == 43200
    assert rot(tz=120).remaining_seconds(0) == 79200


def test_next_reset_timestamp():
    west = rot(tz=-300)
    assert west.next_reset(0) == 18000
    assert west.next_reset(17999) == 18000
    assert rot().next_reset(43200) == 86400


def test_slots_larger_than_pool_rejected():
    with pytest.raises(ValueError):
        sr.ShopRotation(["a", "b", "c"], 4, 1)


def test_duplicate_pool_items_rejected():
    with pytest.raises(ValueError):
        sr.ShopRotation(["a", "b", "b"], 2, 1)


def test_non_positive_slots_rejected():
    with pytest.raises(ValueError):
        sr.ShopRotation(POOL, 0, 1)


def test_timezone_offset_out_of_range_rejected():
    with pytest.raises(ValueError):
        sr.ShopRotation(POOL, 5, 1, tz_offset_minutes=900)
    with pytest.raises(ValueError):
        sr.ShopRotation(POOL, 5, 1, tz_offset_minutes=-900)


def test_returned_rotation_is_independent():
    r = rot()
    items = r.rotation_for(9)
    items.append("junk")
    assert len(r.rotation_for(9)) == 5
    assert "junk" not in r.rotation_for(9)

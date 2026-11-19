import pytest

import auction_house as ah


def house():
    return ah.AuctionHouse(0.1)


def listed():
    game = house()
    game.list_item("a1", "seller", "sword", 10, 100, 0, 10)
    return game


def test_list_creates_auction():
    assert listed().state()["auctions"]["a1"]["status"] == "open"


def test_duplicate_id_raises():
    game = listed()
    with pytest.raises(ValueError):
        game.list_item("a1", "seller", "shield", 10, 100, 0, 10)


def test_seller_cannot_bid():
    game = listed()
    with pytest.raises(ValueError):
        game.bid("a1", "seller", 20, 1)


def test_bid_below_start_raises():
    game = listed()
    with pytest.raises(ValueError):
        game.bid("a1", "buyer", 9, 1)


def test_bid_at_start_is_accepted():
    game = listed()
    game.bid("a1", "buyer", 10, 1)
    assert game.state()["auctions"]["a1"]["current"] == 10


def test_next_bid_must_be_higher():
    game = listed()
    game.bid("a1", "buyer1", 10, 1)
    with pytest.raises(ValueError):
        game.bid("a1", "buyer2", 10, 2)


def test_higher_bid_replaces_current():
    game = listed()
    game.bid("a1", "buyer1", 10, 1)
    game.bid("a1", "buyer2", 20, 2)
    assert game.state()["auctions"]["a1"]["current"] == 20


def test_buyout_closes_immediately():
    game = listed()
    game.bid("a1", "buyer", 100, 1)
    assert game.state()["auctions"]["a1"]["status"] == "sold"


def test_bid_after_sold_raises():
    game = listed()
    game.bid("a1", "buyer", 100, 1)
    with pytest.raises(ValueError):
        game.bid("a1", "other", 110, 2)


def test_expired_auction_settles_to_highest():
    game = listed()
    game.bid("a1", "buyer", 20, 1)
    game.settle(11)
    assert game.state()["auctions"]["a1"]["status"] == "sold"


def test_expired_without_bid_is_unsold():
    game = listed()
    game.settle(11)
    assert game.state()["auctions"]["a1"]["status"] == "unsold"


def test_fee_is_deducted_from_seller():
    game = listed()
    game.bid("a1", "buyer", 20, 1)
    result = game.settle(11)
    assert result[0]["seller_receives"] == pytest.approx(18)


def test_invalid_buyout_raises():
    game = house()
    with pytest.raises(ValueError):
        game.list_item("a1", "seller", "sword", 10, 5, 0, 10)


def test_invalid_duration_raises():
    game = house()
    with pytest.raises(ValueError):
        game.list_item("a1", "seller", "sword", 10, 100, 0, 0)


def test_state_returns_a_copy():
    game = listed()
    snapshot = game.state()
    snapshot["auctions"]["a1"]["status"] = "hacked"
    assert game.state()["auctions"]["a1"]["status"] == "open"

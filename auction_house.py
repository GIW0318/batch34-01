class AuctionHouse:
    def __init__(self, fee_rate=0.05):
        self.fee_rate = fee_rate
        self.auctions = {}

    def list_item(self, auction_id, seller, item, start, buyout, now, duration):
        return None

    def bid(self, auction_id, bidder, amount, now):
        return None

    def settle(self, now):
        return []

    def state(self):
        return {}

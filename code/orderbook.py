from collections import deque


class LimitOrderBook:

    def __init__(self):

        self.bids = deque()  # buyers
        self.asks = deque()  # sellers

        self.best_bid = None
        self.best_ask = None

    def update_market(self, price):

        spread = price * 0.0002  # 2 bps synthetic spread

        self.best_bid = price - spread
        self.best_ask = price + spread

    def add_order(self, order):

        if order.side == "BUY":
            self.bids.append(order)

        elif order.side == "SELL":
            self.asks.append(order)

    def match(self):

        fills = []

        while self.bids and self.asks:

            buy = self.bids[0]
            sell = self.asks[0]

            if buy.price >= sell.price:

                trade_price = (buy.price + sell.price) / 2

                buy.price = trade_price
                sell.price = trade_price

                fills.append(buy)
                fills.append(sell)

                self.bids.popleft()
                self.asks.popleft()

            else:
                break

        return fills

    def execute_market(self, order):

        if order.side == "BUY":
            order.price = self.best_ask

        elif order.side == "SELL":
            order.price = self.best_bid

        return order
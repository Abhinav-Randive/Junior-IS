import random
from collections import deque


class LimitOrderBook:

    def __init__(self):

        self.buy_queue = deque()
        self.sell_queue = deque()

        self.best_bid = None
        self.best_ask = None

    def update_market(self, price):

        spread = price * 0.0002

        self.best_bid = price - spread
        self.best_ask = price + spread

    def submit_order(self, order):

        if order.side == "BUY":
            self.buy_queue.append(order)

        else:
            self.sell_queue.append(order)

    def process_orders(self):

        fills = []

        while self.buy_queue and self.sell_queue:

            buy = self.buy_queue[0]
            sell = self.sell_queue[0]

            if buy.price >= sell.price:

                # simulating queue priority
                if random.random() < 0.7:  # 70% fill probability
                    trade_price = (buy.price + sell.price) / 2

                    buy.price = trade_price
                    sell.price = trade_price

                    fills.append(buy)
                    fills.append(sell)

                    self.buy_queue.popleft()
                    self.sell_queue.popleft()

                else:
                    break

            else:
                break

        return fills
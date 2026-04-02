from collections import deque
from fill import Fill


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

                trade_price = sell.price   # buyer pays ask

                fills.append(Fill("BUY", trade_price, buy.quantity, buy.timestamp))
                fills.append(Fill("SELL", trade_price, sell.quantity, sell.timestamp))

                self.buy_queue.popleft()
                self.sell_queue.popleft()

            else:
                break

        return fills
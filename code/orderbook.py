from collections import deque
import hashlib

from fill import Fill


class LimitOrderBook:

    def __init__(self):

        self.buy_queue = deque()
        self.sell_queue = deque()

        self.best_bid = None
        self.best_ask = None
        self.buy_liquidity = 0
        self.sell_liquidity = 0

    def update_market(self, price, quantity=1):

        spread = price * 0.0002
        self.best_bid = price - spread
        self.best_ask = price + spread

        traded_quantity = max(1, int(float(quantity)))
        self.buy_liquidity = max(1, traded_quantity // 2)
        self.sell_liquidity = max(1, traded_quantity - self.buy_liquidity)

    def submit_order(self, order):

        if order.side == "BUY":
            self.buy_queue.append(order)
        else:
            self.sell_queue.append(order)

    def _score_order(self, order):
        basis = (
            f"{order.order_id}:{order.timestamp}:{order.remaining_quantity}:"
            f"{self.best_bid}:{self.best_ask}"
        )
        digest = hashlib.sha256(basis.encode("ascii")).hexdigest()
        return int(digest[:8], 16) / 0xFFFFFFFF

    def _crosses_market(self, order):
        if order.side == "BUY":
            return self.best_ask is not None and order.price >= self.best_ask
        return self.best_bid is not None and order.price <= self.best_bid

    def _process_queue(self, queue, side, probability_model):
        fills = []

        if side == "BUY":
            trade_price = self.best_ask
            available_liquidity = self.sell_liquidity
        else:
            trade_price = self.best_bid
            available_liquidity = self.buy_liquidity

        queue_position = 0
        while queue and available_liquidity > 0:
            order = queue[0]

            if not self._crosses_market(order):
                break

            fill_probability = probability_model(order, queue_position)
            if self._score_order(order) > fill_probability:
                break

            fill_quantity = min(order.remaining_quantity, available_liquidity)
            fills.append(
                Fill(
                    side=order.side,
                    price=trade_price,
                    quantity=fill_quantity,
                    timestamp=order.timestamp,
                    order_id=order.order_id,
                )
            )

            order.remaining_quantity -= fill_quantity
            available_liquidity -= fill_quantity

            if order.remaining_quantity == 0:
                queue.popleft()
            else:
                break

            queue_position += 1

        if side == "BUY":
            self.sell_liquidity = available_liquidity
        else:
            self.buy_liquidity = available_liquidity

        return fills

    def process_orders(self, probability_model):

        fills = []
        fills.extend(self._process_queue(self.buy_queue, "BUY", probability_model))
        fills.extend(self._process_queue(self.sell_queue, "SELL", probability_model))

        return fills

from fill import Fill

class ExecutionEngine:

    def __init__(self, orderbook, fee=0.005, slippage=0.0002):
        self.orderbook = orderbook
        self.fee = fee 
        self.slippage = slippage

    def submit(self, order):
        self.orderbook.submit_order(order)

    def _fill_probability(self, order, queue_position):
        if order.side == "BUY" and self.orderbook.best_ask:
            reference_price = self.orderbook.best_ask
            aggressiveness = max(0.0, (order.price - reference_price) / reference_price)
        else:
            reference_price = self.orderbook.best_bid
            aggressiveness = (
                max(0.0, (reference_price - order.price) / reference_price)
                if reference_price else 0.0
            )

        base_probability = 0.35
        queue_penalty = queue_position * 0.12
        aggression_bonus = min(0.45, aggressiveness * 500)
        return max(0.05, min(0.95, base_probability + aggression_bonus - queue_penalty))

    def _apply_execution_costs(self, fill):
        price = fill.price
        if fill.side == "BUY":
            price *= (1 + self.slippage)
        else:
            price *= (1 - self.slippage)

        return Fill(
            side=fill.side,
            price=price,
            quantity=fill.quantity,
            timestamp=fill.timestamp,
            order_id=fill.order_id,
            fee=self.fee * fill.quantity,
        )

    def process_market(self):
        fills = self.orderbook.process_orders(self._fill_probability)
        return [self._apply_execution_costs(fill) for fill in fills]

    def execute(self, order):
        self.submit(order)
        return self.process_market()

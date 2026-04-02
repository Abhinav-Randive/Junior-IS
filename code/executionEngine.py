from fill import Fill

class ExecutionEngine:

    def __init__(self, orderbook):
        self.orderbook = orderbook

    def execute(self, order):

        # simulate immediate market execution
        if order.side == "BUY":
            price = self.orderbook.best_ask
        else:
            price = self.orderbook.best_bid

        fill = Fill(
            side=order.side,
            price=price,
            quantity=order.quantity,
            timestamp=order.timestamp
        )

        return [fill]
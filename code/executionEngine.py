from fill import Fill

class ExecutionEngine:

    def __init__(self, orderbook, fee =0.005, slippage =0.0002):
        self.orderbook = orderbook
        self.fee = fee 
        self.slippage = slippage

    def execute(self, order):

        # simulate immediate market execution
        if order.side == "BUY":
            price = self.orderbook.best_ask
        else:
            price = self.orderbook.best_bid
        
        # apply slippage + txn costs
        if order.side == "BUY":
            price *= (1 + self.slippage)
        else:
            price *= (1 - self.slippage)


        fill = Fill(
            side=order.side,
            price=price,
            quantity=order.quantity,
            timestamp=order.timestamp
        )

        return [fill]
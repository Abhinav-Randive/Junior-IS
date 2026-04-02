class ExecutionEngine:

    def __init__(self, orderbook):

        self.orderbook = orderbook

    def execute(self, order):

        self.orderbook.submit_order(order)

        fills = self.orderbook.process_orders()

        return fills
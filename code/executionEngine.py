class ExecutionEngine:

    def __init__(self, orderbook):

        self.orderbook = orderbook

    def execute(self, order):

        # Simulate market order
        fill = self.orderbook.execute_market(order)

        return fill
class Portfolio:

    def __init__(self, max_position=10):

        self.position = 0
        self.cash = 0
        self.max_position = max_position

        self.history = []  # equity curve
        self.trades = []

    def can_buy(self):
        return self.position < self.max_position

    def can_sell(self):
        return self.position > -self.max_position

    def update(self, fill, market_price):
        trade_value = fill.price * fill.quantity
        total_cost = trade_value + fill.fee

        if fill.side == "BUY" and self.can_buy():
            self.position += fill.quantity
            self.cash -= total_cost

        elif fill.side == "SELL" and self.can_sell():
            self.position -= fill.quantity
            self.cash += trade_value - fill.fee

        self.trades.append(fill)

        # track portfolio value over time
        value = self.cash + self.position * market_price
        self.history.append(value)

    def value(self, price):
        return self.cash + self.position * price

    def summary(self):

        print("\nPortfolio Summary")
        print("Position:", self.position)
        print("Cash:", round(self.cash, 2))
        print("Total Trades:", len(self.trades))

class Portfolio:

    def __init__(self, max_position=10, starting_capital=100000):
        self.position = 0
        self.cash = starting_capital
        self.max_position = max_position

        self.history = []
        self.trades = []
        self.metrics = []

    def can_buy(self, quantity=1):
        return (self.position + quantity <= self.max_position) and (self.cash >= 0)

    def can_sell(self, quantity=1):
        return (self.position >= quantity) and (self.position - quantity >= -self.max_position)

    def update(self, fill, market_price, event_index):  # 🔥 NEW ARG
        trade_value = fill.price * fill.quantity
        total_cost = trade_value + fill.fee

        if fill.side == "BUY" and self.can_buy(fill.quantity):
            self.position += fill.quantity
            self.cash -= total_cost

        elif fill.side == "SELL" and self.can_sell(fill.quantity):
            self.position -= fill.quantity
            self.cash += trade_value - fill.fee

        self.trades.append(fill)

        value = self.cash + self.position * market_price
        self.history.append(value)

        # 🔥 aligned metrics
        self.metrics.append({
            "event_index": event_index,
            "timestamp": fill.timestamp,
            "side": fill.side,
            "price": fill.price,
            "market_price": market_price,
            "quantity": fill.quantity,
            "position": self.position,
            "cash": self.cash,
            "value": value
        })

    def value(self, price):
        return self.cash + self.position * price

    def summary(self):
        print("\nPortfolio Summary")
        print("Position:", self.position)
        print("Cash:", round(self.cash, 2))
        print("Total Trades:", len(self.trades))
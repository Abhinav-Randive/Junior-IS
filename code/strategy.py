class SimpleStrategy:

    def __init__(self, short=5, long=20):
        self.prices = []
        self.short = short
        self.long = long

    def on_market_update(self, event, portfolio):

        price = float(event.payload["price"])
        self.prices.append(price)

        if len(self.prices) < self.long:
            return None

        short_ma = sum(self.prices[-self.short:]) / self.short
        long_ma = sum(self.prices[-self.long:]) / self.long

        if short_ma > long_ma and portfolio.position <= 0:
            return "BUY"

        if short_ma < long_ma and portfolio.position >= 0:
            return "SELL"

        return None
class SimpleStrategy:
    def __init__(self):
        self.last_price = None
        self.buy_signals = 0
        self.sell_signals = 0

    def on_market_update(self, event):

        price = float(event.payload["price"])

        if self.last_price is None:
            self.last_price = price
            return None

        signal = None

        if price > self.last_price:
            signal = "BUY"
            self.buy_signals += 1

        elif price < self.last_price:
            signal = "SELL"
            self.sell_signals += 1

        self.last_price = price

        return signal
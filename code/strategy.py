class SimpleStrategy:

    def __init__(self, window=10):

        self.prices = []
        self.window = window

    def on_market_update(self, event):

        price = float(event.payload["price"])

        self.prices.append(price)

        if len(self.prices) < self.window:
            return None

        moving_avg = sum(self.prices[-self.window:]) / self.window

        if price > moving_avg:
            return "BUY"

        if price < moving_avg:
            return "SELL"

        return None
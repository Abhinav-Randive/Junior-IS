from collections import deque
from math import exp, sqrt


class BaselineSignalModel:

    def __init__(self, short_window=5, long_window=20, volume_window=20):
        self.short_window = short_window
        self.long_window = long_window
        self.volume_window = volume_window

        self.prices = deque(maxlen=long_window)
        self.volumes = deque(maxlen=volume_window)
        self.returns = deque(maxlen=long_window)
        self.previous_price = None

    def ready(self):
        return (
            len(self.prices) >= self.long_window
            and len(self.volumes) >= self.volume_window
            and len(self.returns) >= self.short_window
        )

    def _safe_mean(self, values):
        return sum(values) / len(values) if values else 0.0

    def _safe_std(self, values, mean):
        if len(values) < 2:
            return 0.0

        variance = sum((value - mean) ** 2 for value in values) / len(values)
        return sqrt(variance)

    def update(self, event):
        price = float(event.payload["price"])
        volume = float(event.payload.get("quantity", 0))

        if self.previous_price not in (None, 0):
            price_return = (price - self.previous_price) / self.previous_price
            self.returns.append(price_return)

        self.previous_price = price
        self.prices.append(price)
        self.volumes.append(volume)

    def _build_features(self):
        short_prices = list(self.prices)[-self.short_window:]
        long_prices = list(self.prices)
        recent_returns = list(self.returns)[-self.short_window:]
        recent_volumes = list(self.volumes)

        short_ma = self._safe_mean(short_prices)
        long_ma = self._safe_mean(long_prices)
        momentum = (short_ma - long_ma) / long_ma if long_ma else 0.0

        last_return = recent_returns[-1] if recent_returns else 0.0

        return_mean = self._safe_mean(recent_returns)
        volatility = self._safe_std(recent_returns, return_mean)

        volume_mean = self._safe_mean(recent_volumes)
        volume_std = self._safe_std(recent_volumes, volume_mean)
        volume_surprise = (
            (recent_volumes[-1] - volume_mean) / volume_std
            if volume_std > 0 else 0.0
        )

        return {
            "momentum": momentum,
            "last_return": last_return,
            "volatility": volatility,
            "volume_surprise": volume_surprise,
        }

    def predict(self, event):
        self.update(event)

        if not self.ready():
            return {
                "signal_strength": 0.0,
                "prob_up": 0.5,
                "features": None,
            }

        features = self._build_features()

        linear_score = (
            180.0 * features["momentum"]
            + 90.0 * features["last_return"]
            - 25.0 * features["volatility"]
            + 0.08 * features["volume_surprise"]
        )
        probability_up = 1.0 / (1.0 + exp(-linear_score))

        return {
            "signal_strength": (probability_up - 0.5) * 2.0,
            "prob_up": probability_up,
            "features": features,
        }

from collections import deque
from math import exp, sqrt


class BaselineSignalModel:
    """Enhanced signal model with multiple technical indicators"""

    def __init__(self, short_window=5, long_window=20, volume_window=20, rsi_window=14):
        self.short_window = short_window
        self.long_window = long_window
        self.volume_window = volume_window
        self.rsi_window = rsi_window

        self.prices = deque(maxlen=long_window)
        self.volumes = deque(maxlen=volume_window)
        self.returns = deque(maxlen=long_window)
        self.gains = deque(maxlen=rsi_window)
        self.losses = deque(maxlen=rsi_window)
        self.previous_price = None

    def ready(self):
        return (
            len(self.prices) >= self.long_window
            and len(self.volumes) >= self.volume_window
            and len(self.returns) >= self.short_window
            and len(self.gains) >= self.rsi_window
        )

    def _safe_mean(self, values):
        return sum(values) / len(values) if values else 0.0

    def _safe_std(self, values, mean):
        if len(values) < 2:
            return 0.0
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        return sqrt(variance)

    def _calculate_sma(self, prices, period):
        """Simple Moving Average"""
        if len(prices) < period:
            return self._safe_mean(prices)
        return self._safe_mean(list(prices)[-period:])

    def _calculate_rsi(self):
        """Relative Strength Index"""
        if len(self.gains) < self.rsi_window or len(self.losses) < self.rsi_window:
            return 50.0

        avg_gain = self._safe_mean(self.gains)
        avg_loss = self._safe_mean(self.losses)

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        rsi = 100.0 - (100.0 / (1.0 + rs))
        return rsi

    def _calculate_bollinger_bands(self, prices, period=20):
        """Bollinger Bands"""
        if len(prices) < period:
            return 0.0, 0.0, 0.0

        prices_list = list(prices)[-period:]
        middle = self._safe_mean(prices_list)
        std = self._safe_std(prices_list, middle)

        upper = middle + (std * 2)
        lower = middle - (std * 2)

        # Return position relative to bands (-1 to 1)
        if upper == lower:
            return 0.0, middle, upper

        position = (prices_list[-1] - lower) / (upper - lower)
        position = max(-1.0, min(1.0, position * 2 - 1))  # Normalize to -1..1

        return position, middle, upper

    def _calculate_macd(self):
        """MACD (Moving Average Convergence Divergence)"""
        if len(self.prices) < 26:
            return 0.0

        prices = list(self.prices)
        ema_12 = self._calculate_ema(prices, 12)
        ema_26 = self._calculate_ema(prices, 26)
        macd = ema_12 - ema_26

        return macd

    def _calculate_ema(self, prices, period):
        """Exponential Moving Average"""
        if not prices or period < 1:
            return self._safe_mean(prices) if prices else 0.0

        multiplier = 2.0 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    def update(self, event):
        price = float(event.payload["price"])
        volume = float(event.payload.get("quantity", 0))

        if self.previous_price not in (None, 0):
            price_return = (price - self.previous_price) / self.previous_price
            self.returns.append(price_return)

            # Update gains and losses for RSI
            if price_return > 0:
                self.gains.append(price_return)
                self.losses.append(0)
            else:
                self.gains.append(0)
                self.losses.append(abs(price_return))

        self.previous_price = price
        self.prices.append(price)
        self.volumes.append(volume)

    def _build_features(self):
        short_prices = list(self.prices)[-self.short_window:]
        long_prices = list(self.prices)
        recent_returns = list(self.returns)[-self.short_window:]
        recent_volumes = list(self.volumes)

        # Momentum
        short_ma = self._safe_mean(short_prices)
        long_ma = self._safe_mean(long_prices)
        momentum = (short_ma - long_ma) / long_ma if long_ma else 0.0

        last_return = recent_returns[-1] if recent_returns else 0.0

        # Volatility
        return_mean = self._safe_mean(recent_returns)
        volatility = self._safe_std(recent_returns, return_mean)

        # Volume
        volume_mean = self._safe_mean(recent_volumes)
        volume_std = self._safe_std(recent_volumes, volume_mean)
        volume_surprise = (
            (recent_volumes[-1] - volume_mean) / volume_std if volume_std > 0 else 0.0
        )

        # RSI
        rsi = self._calculate_rsi()
        rsi_signal = (rsi - 50.0) / 50.0  # Normalize to -1..1

        # Bollinger Bands
        bb_position, bb_middle, bb_upper = self._calculate_bollinger_bands(
            self.prices, 20
        )

        # MACD
        macd = self._calculate_macd()

        return {
            "momentum": momentum,
            "last_return": last_return,
            "volatility": volatility,
            "volume_surprise": volume_surprise,
            "rsi": rsi,
            "rsi_signal": rsi_signal,
            "bb_position": bb_position,
            "macd": macd,
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

        # Enhanced linear score with multiple indicators (normalized coefficients)
        linear_score = (
            1.8 * features["momentum"]  # Reduced from 180
            + 0.9 * features["last_return"]  # Reduced from 90
            - 0.25 * features["volatility"]  # Reduced from 25
            + 0.08 * features["volume_surprise"]
            + 0.5 * features["rsi_signal"]  # Reduced from 50
            + 1.0 * features["bb_position"]  # Reduced from 100
            + 0.05 * features["macd"]  # Reduced from 5
        )

        # Clip linear_score to prevent numerical overflow
        linear_score = max(-10.0, min(10.0, linear_score))

        try:
            probability_up = 1.0 / (1.0 + exp(-linear_score))
        except (OverflowError, ValueError):
            probability_up = 0.0 if linear_score < 0 else 1.0

        signal_strength = (probability_up - 0.5) * 2.0

        # Ensure signal_strength is bounded and not NaN
        if not (-1.0 <= signal_strength <= 1.0) or signal_strength != signal_strength:
            signal_strength = 0.0

        return {
            "signal_strength": signal_strength,
            "prob_up": probability_up,
            "features": features,
        }

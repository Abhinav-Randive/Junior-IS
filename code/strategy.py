class PredictionStrategy:

    def __init__(self, signal_model, entry_threshold=0.06):
        self.signal_model = signal_model
        self.entry_threshold = entry_threshold
        self.last_prediction = None

    def on_market_update(self, event, portfolio):
        prediction = self.signal_model.predict(event)
        self.last_prediction = prediction

        signal_strength = prediction["signal_strength"]

        if signal_strength >= self.entry_threshold and portfolio.position <= 0:
            return {
                "side": "BUY",
                "strength": signal_strength,
                "prob_up": prediction["prob_up"],
            }

        if signal_strength <= -self.entry_threshold and portfolio.position >= 0:
            return {
                "side": "SELL",
                "strength": abs(signal_strength),
                "prob_up": prediction["prob_up"],
            }

        return None

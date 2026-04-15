from order import Order


class OrderManager:
    def __init__(self):
        self._next_order_id = 1

    def create_order(self, signal, event):
        side = signal["side"]
        strength = max(0.0, min(1.0, float(signal.get("strength", 0.0))))

        price = float(event.payload["price"])
        quantity = max(1, min(3, int(1 + strength * 2)))
        price_offset = 0.00015 + (strength * 0.0015)

        if side == "BUY":
            price *= 1 + price_offset
        else:
            price *= 1 - price_offset

        order = Order(
            side=side,
            price=price,
            quantity=quantity,
            timestamp=event.timestamp,
            order_id=self._next_order_id,
        )
        self._next_order_id += 1
        return order

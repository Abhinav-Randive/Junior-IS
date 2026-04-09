from order import Order


class OrderManager:
    def __init__(self):
        self._next_order_id = 1

    def create_order(self, signal, event):

        price = float(event.payload["price"])

        if signal == "BUY":
            price *= 0.999   # buy cheaper
        else:
            price *= 1.001   # sell higher

        order = Order(
            side=signal,
            price=price,
            quantity=1,
            timestamp=event.timestamp,
            order_id=self._next_order_id,
        )
        self._next_order_id += 1
        return order

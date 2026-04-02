from order import Order


class OrderManager:
    def create_order(self, signal, event):

        price = float(event.payload["price"])

        if signal == "BUY":
            price *= 0.999   # buy cheaper
        else:
            price *= 1.001   # sell higher

        return Order(
            side=signal,
            price=price,
            quantity=1,
            timestamp=event.timestamp
        )
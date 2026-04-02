from order import Order


class OrderManager:

    def create_order(self, signal, event):

        price = float(event.payload["price"])

        return Order(
            side=signal,
            price=price,
            quantity=1,
            timestamp=event.timestamp
        )
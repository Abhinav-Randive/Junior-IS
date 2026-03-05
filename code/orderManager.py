from order import Order

class OrderManager:

    def create_order(self, signal, event):

        price = float(event.payload["price"])

        if signal == "BUY":
            return Order("BUY", price, 1)

        if signal == "SELL":
            return Order("SELL", price, 1)

        return None
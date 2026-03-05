class Portfolio:

    def __init__(self):
        self.position = 0
        self.cash = 0
    
    def update(self, order):
        if order.side == "BUY":
            self.position += order.quantity
            self.cash -= order.price * order.quantity

        elif order.side == "SELL":
            self.position -= order.quantity
            self.cash += order.price * order.quantity

    def summary(self):
        print("\nPortfolio Summary")
        print("Position:", self.position)
        print("Cash:", round(self.cash, 2))
        
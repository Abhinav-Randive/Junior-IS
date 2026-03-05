class Portfolio:

    def __init__(self, max_position=10):

        self.position = 0
        self.cash = 0
        self.max_position = max_position

    def can_buy(self):

        return self.position < self.max_position

    def can_sell(self):

        return self.position > -self.max_position

    def update(self, order):

        if order.side == "BUY" and self.can_buy():

            self.position += order.quantity
            self.cash -= order.price * order.quantity

        elif order.side == "SELL" and self.can_sell():

            self.position -= order.quantity
            self.cash += order.price * order.quantity

    def value(self, price):

        return self.cash + self.position * price

    def summary(self):

        print("\nPortfolio Summary")
        print("Position:", self.position)
        print("Cash:", round(self.cash, 2))
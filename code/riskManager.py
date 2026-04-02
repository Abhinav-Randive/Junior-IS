class RiskManager:

    def approve(self, order, portfolio):

        if order.side == "BUY" and not portfolio.can_buy():
            return False

        if order.side == "SELL" and not portfolio.can_sell():
            return False

        return True
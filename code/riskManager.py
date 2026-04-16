class RiskManager:
    """Risk management for trading positions"""

    def __init__(
        self,
        max_position=10,
        max_loss_per_trade=0.02,  # 2% of capital
        max_daily_loss=0.05,  # 5% of capital
        max_portfolio_heat=0.10,  # 10% of capital at risk
        position_size_limit=0.5,  # Max 50% of capital per trade
    ):
        self.max_position = max_position
        self.max_loss_per_trade = max_loss_per_trade
        self.max_daily_loss = max_daily_loss
        self.max_portfolio_heat = max_portfolio_heat
        self.position_size_limit = position_size_limit
        self.daily_losses = 0.0
        self.initial_capital = 100000

    def reset_daily_losses(self):
        """Reset daily loss counter (called once per day)"""
        self.daily_losses = 0.0

    def _calculate_trade_risk(self, order, portfolio, market_price):
        """Calculate potential loss for a proposed trade"""
        if order.side == "BUY":
            # Risk = (entry_price - stop_loss) * quantity
            # Assume stop loss is 2% below entry
            stop_loss = order.price * 0.98
            risk = (order.price - stop_loss) * order.quantity
        else:  # SELL
            # Risk = (stop_loss - entry_price) * quantity
            stop_loss = order.price * 1.02
            risk = (stop_loss - order.price) * order.quantity

        return abs(risk)

    def _calculate_position_size(self, portfolio, market_price, volatility=0.02):
        """Calculate appropriate position size based on volatility"""
        available_capital = portfolio.cash
        max_risk_per_trade = self.initial_capital * self.max_loss_per_trade

        # Position size = max_risk / (price * stop_loss_percent)
        if market_price > 0:
            position_size = max_risk_per_trade / (market_price * 0.02)
            position_size = min(position_size, self.max_position)
            position_size = int(max(1, position_size))
        else:
            position_size = 1

        return position_size

    def approve(self, order, portfolio, market_price=None):
        """Comprehensive risk approval check"""

        # 1. Check position limits
        if order.side == "BUY" and not portfolio.can_buy(order.quantity):
            return False

        if order.side == "SELL" and not portfolio.can_sell(order.quantity):
            return False

        # 2. Check daily loss limit
        if self.daily_losses >= self.initial_capital * self.max_daily_loss:
            return False

        # 3. Check cash availability for buys
        if order.side == "BUY":
            trade_cost = order.price * order.quantity * 1.005  # Estimate with fees
            if portfolio.cash < trade_cost:
                return False

        # 4. Calculate portfolio heat (risk exposure)
        current_heat = abs(portfolio.position * market_price) if market_price else 0
        if current_heat > self.initial_capital * self.max_portfolio_heat:
            return False

        return True

    def update_daily_losses(self, pnl):
        """Track daily losses"""
        if pnl < 0:
            self.daily_losses += abs(pnl)
from fill import Fill

class ExecutionEngine:
    """Execution engine with realistic transaction costs modeling"""

    def __init__(
        self,
        orderbook,
        fee=0.001,  # 0.1% commission
        base_slippage=0.0002,  # 0.02% base slippage
        market_impact_factor=0.001,  # Market impact per unit
    ):
        self.orderbook = orderbook
        self.fee = fee
        self.base_slippage = base_slippage
        self.market_impact_factor = market_impact_factor

    def submit(self, order):
        self.orderbook.submit_order(order)

    def _fill_probability(self, order, queue_position):
        if order.side == "BUY":
            reference_price = self.orderbook.best_ask or 0.0001
            aggressiveness = (
                max(0.0, (order.price - reference_price) / reference_price)
                if reference_price > 0
                else 0.0
            )
        else:  # SELL
            reference_price = self.orderbook.best_bid
            aggressiveness = (
                max(0.0, (reference_price - order.price) / reference_price)
                if reference_price
                else 0.0
            )

        base_probability = 0.35
        queue_penalty = queue_position * 0.12
        aggression_bonus = min(0.45, aggressiveness * 500)
        return max(0.05, min(0.95, base_probability + aggression_bonus - queue_penalty))

    def _calculate_dynamic_slippage(self, fill):
        """Calculate slippage based on order size and market conditions"""
        # Larger orders get worse slippage
        size_impact = (fill.quantity / 100.0) * 0.0001  # 0.01% per 100 shares
        return self.base_slippage + size_impact

    def _calculate_market_impact(self, fill):
        """Calculate market impact cost for large orders"""
        # Market impact: sqrt(Q/V) * price * impact_factor
        # Q = order quantity, V = typical volume
        typical_volume = 1000  # Assume 1000 share typical volume
        impact = (
            (fill.quantity / typical_volume) ** 0.5
            * fill.price
            * self.market_impact_factor
        )
        return impact

    def _calculate_total_cost(self, fill):
        """Calculate all transaction costs"""
        # Commission
        commission = self.fee * fill.price * fill.quantity

        # Slippage
        slippage = self._calculate_dynamic_slippage(fill)
        slippage_cost = slippage * fill.price * fill.quantity

        # Market impact (one-way)
        market_impact = self._calculate_market_impact(fill)

        total_cost = commission + slippage_cost + market_impact
        return total_cost, commission, slippage_cost, market_impact

    def _apply_execution_costs(self, fill):
        # Base slippage
        price = fill.price
        slippage_pct = self._calculate_dynamic_slippage(fill)

        if fill.side == "BUY":
            price *= 1 + slippage_pct
        else:
            price *= 1 - slippage_pct

        # Calculate total costs
        total_cost, commission, slippage_cost, market_impact = self._calculate_total_cost(
            fill
        )

        # Total fee includes commission + slippage + market impact
        total_fee = commission + slippage_cost + market_impact

        return Fill(
            side=fill.side,
            price=price,
            quantity=fill.quantity,
            timestamp=fill.timestamp,
            order_id=fill.order_id,
            fee=total_fee,
        )

    def process_market(self):
        fills = self.orderbook.process_orders(self._fill_probability)
        return [self._apply_execution_costs(fill) for fill in fills]

    def execute(self, order):
        self.submit(order)
        return self.process_market()

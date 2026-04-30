"""
Execution Analysis Tool - Analyze fill quality, slippage, and market impact
"""


class ExecutionAnalyzer:
    """Analyzes execution quality and market microstructure dynamics"""

    def __init__(self, portfolio, market_data):
        self.portfolio = portfolio
        self.market_data = market_data
        self.trades = portfolio.trades
        self.metrics = portfolio.metrics

    def analyze_slippage(self):
        """Analyze execution slippage vs reference prices"""
        if not self.trades:
            return {}

        slippage_data = []
        for i, trade in enumerate(self.trades):
            # Reference: best bid for sells, best ask for buys
            ref_price = trade.price * 0.98 if trade.side == "BUY" else trade.price * 1.02
            slippage = abs(trade.price - ref_price)
            slippage_pct = (slippage / ref_price * 100) if ref_price else 0

            slippage_data.append({
                "order_id": trade.order_id,
                "side": trade.side,
                "price": trade.price,
                "reference_price": ref_price,
                "slippage": slippage,
                "slippage_pct": slippage_pct,
            })

        avg_slippage = sum(s["slippage"] for s in slippage_data) / len(slippage_data)
        avg_slippage_pct = sum(s["slippage_pct"] for s in slippage_data) / len(slippage_data)

        return {
            "trades": slippage_data,
            "avg_slippage": avg_slippage,
            "avg_slippage_pct": avg_slippage_pct,
            "total_slippage_cost": sum(s["slippage"] * t.quantity for s, t in zip(slippage_data, self.trades)),
        }

    def analyze_fill_rates(self):
        """Analyze order fill success rates"""
        buy_orders = [t for t in self.trades if t.side == "BUY"]
        sell_orders = [t for t in self.trades if t.side == "SELL"]

        return {
            "total_orders": len(self.trades),
            "buy_orders": len(buy_orders),
            "sell_orders": len(sell_orders),
            "fill_rate": len(self.trades) / max(len(self.trades), 1),
            "avg_order_size": sum(t.quantity for t in self.trades) / len(self.trades) if self.trades else 0,
        }

    def analyze_market_impact(self):
        """Estimate market impact from trades"""
        if not self.trades:
            return {}

        impact_data = []
        total_traded_value = 0
        total_impact_cost = 0

        for trade in self.trades:
            # Market impact = sqrt(Q/V) * price * impact_factor
            typical_volume = 1000
            impact_factor = 0.001
            
            impact = (trade.quantity / typical_volume) ** 0.5 * trade.price * impact_factor
            impact_cost = impact * trade.quantity

            total_traded_value += trade.price * trade.quantity
            total_impact_cost += impact_cost

            impact_data.append({
                "order_id": trade.order_id,
                "quantity": trade.quantity,
                "price": trade.price,
                "impact_cost": impact_cost,
                "impact_pct": (impact_cost / (trade.price * trade.quantity)) * 100 if trade.price else 0,
            })

        return {
            "trades": impact_data,
            "total_traded_value": total_traded_value,
            "total_impact_cost": total_impact_cost,
            "avg_impact_cost_pct": (total_impact_cost / total_traded_value * 100) if total_traded_value else 0,
        }

    def analyze_timing(self):
        """Analyze execution timing vs market conditions"""
        if not self.metrics:
            return {}

        timing_data = []
        for metric in self.metrics:
            timing_data.append({
                "event_index": metric["event_index"],
                "side": metric["side"],
                "price": metric["price"],
                "market_price": metric["market_price"],
                "slippage_at_execution": abs(metric["price"] - metric["market_price"]),
            })

        return {
            "trades": timing_data,
            "execution_count": len(timing_data),
        }

    def analyze_fees(self):
        """Analyze commission and fee structure"""
        total_fees = sum(t.fee for t in self.trades)
        total_notional = sum(t.price * t.quantity for t in self.trades)
        avg_fee_pct = (total_fees / total_notional * 100) if total_notional else 0

        return {
            "total_fees": total_fees,
            "total_notional_value": total_notional,
            "avg_fee_pct": avg_fee_pct,
            "fee_per_trade": total_fees / len(self.trades) if self.trades else 0,
        }

    def generate_execution_report(self):
        """Generate comprehensive execution analysis"""
        report = {
            "fill_rates": self.analyze_fill_rates(),
            "slippage": self.analyze_slippage(),
            "market_impact": self.analyze_market_impact(),
            "timing": self.analyze_timing(),
            "fees": self.analyze_fees(),
        }
        return report

    def print_execution_report(self):
        """Print formatted execution report"""
        report = self.generate_execution_report()

        print("\n" + "=" * 60)
        print("EXECUTION QUALITY ANALYSIS")
        print("=" * 60)

        # Fill Rates
        fr = report["fill_rates"]
        print(f"\nFILL RATES:")
        print(f"  Total Orders:         {fr['total_orders']}")
        print(f"  Buy Orders:           {fr['buy_orders']}")
        print(f"  Sell Orders:          {fr['sell_orders']}")
        print(f"  Fill Rate:            {fr['fill_rate']*100:.2f}%")
        print(f"  Avg Order Size:       {fr['avg_order_size']:.2f} units")

        # Slippage
        sp = report["slippage"]
        if sp:
            print(f"\nSLIPPAGE ANALYSIS:")
            print(f"  Avg Slippage:         ${sp['avg_slippage']:.4f}")
            print(f"  Avg Slippage %:       {sp['avg_slippage_pct']:.4f}%")
            print(f"  Total Slippage Cost:  ${sp['total_slippage_cost']:.2f}")

        # Market Impact
        mi = report["market_impact"]
        if mi:
            print(f"\nMARKET IMPACT:")
            print(f"  Total Traded Value:   ${mi['total_traded_value']:.2f}")
            print(f"  Total Impact Cost:    ${mi['total_impact_cost']:.2f}")
            print(f"  Avg Impact %:         {mi['avg_impact_cost_pct']:.4f}%")

        # Fees
        fe = report["fees"]
        print(f"\nFEES & COMMISSIONS:")
        print(f"  Total Fees Paid:      ${fe['total_fees']:.2f}")
        print(f"  Notional Value:       ${fe['total_notional_value']:.2f}")
        print(f"  Avg Fee %:            {fe['avg_fee_pct']:.4f}%")
        print(f"  Fee Per Trade:        ${fe['fee_per_trade']:.2f}")

        print("\n" + "=" * 60)

        return report

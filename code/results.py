import statistics
import json
from datetime import datetime


class ResultsAnalyzer:
    """Comprehensive analysis of trading simulation results"""

    def __init__(self, portfolio, latency_tracker, last_price, initial_capital=100000):
        self.portfolio = portfolio
        self.latency_tracker = latency_tracker
        self.last_price = last_price
        self.initial_capital = initial_capital

    def calculate_returns(self):
        """Calculate total return and annualized return"""
        final_value = self.portfolio.value(self.last_price)
        total_return = (final_value - self.initial_capital) / self.initial_capital
        return {
            "total_return": total_return,
            "total_return_pct": total_return * 100,
            "final_value": final_value,
        }

    def calculate_sharpe_ratio(self, risk_free_rate=0.02):
        """Calculate Sharpe ratio from equity curve"""
        if len(self.portfolio.history) < 2:
            return 0.0

        # Calculate daily returns
        returns = []
        for i in range(1, len(self.portfolio.history)):
            ret = (self.portfolio.history[i] - self.portfolio.history[i - 1]) / self.portfolio.history[i - 1]
            returns.append(ret)

        if not returns:
            return 0.0

        avg_return = statistics.mean(returns)
        std_return = statistics.stdev(returns) if len(returns) > 1 else 0.0

        if std_return == 0:
            return 0.0

        sharpe = (avg_return - risk_free_rate / 252) / std_return * (252 ** 0.5)
        return sharpe

    def calculate_max_drawdown(self):
        """Calculate maximum drawdown from peak"""
        if not self.portfolio.history:
            return 0.0

        peak = self.portfolio.history[0]
        max_dd = 0.0

        for value in self.portfolio.history:
            if value > peak:
                peak = value
            dd = (peak - value) / peak if peak > 0 else 0
            max_dd = max(max_dd, dd)

        return max_dd

    def calculate_calmar_ratio(self):
        """Calculate Calmar Ratio (Return / Max Drawdown)"""
        ret = self.calculate_returns()
        max_dd = self.calculate_max_drawdown()

        if max_dd == 0:
            return 0.0

        return ret["total_return"] / max_dd

    def calculate_trade_stats(self):
        """Calculate trade-related statistics"""
        trades = self.portfolio.trades
        metrics = self.portfolio.metrics

        if not trades:
            return {
                "total_trades": 0,
                "buy_count": 0,
                "sell_count": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "avg_win": 0.0,
                "avg_loss": 0.0,
                "total_fees": 0.0,
            }

        buy_trades = [t for t in trades if t.side == "BUY"]
        sell_trades = [t for t in trades if t.side == "SELL"]

        # Approximate round-trip P&L by pairing buys and sells in trade order
        # (not a full inventory model; adequate for coarse win-rate summaries)
        pnl_trades = []
        buy_prices = [t.price for t in buy_trades]
        sell_prices = [t.price for t in sell_trades]

        for i in range(min(len(buy_prices), len(sell_prices))):
            pnl = sell_prices[i] - buy_prices[i]
            pnl_trades.append(pnl)

        winning_trades = [p for p in pnl_trades if p > 0]
        losing_trades = [p for p in pnl_trades if p < 0]

        win_rate = len(winning_trades) / len(pnl_trades) if pnl_trades else 0.0

        total_wins = sum(winning_trades) if winning_trades else 0.0
        total_losses = abs(sum(losing_trades)) if losing_trades else 0.0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0.0

        avg_win = statistics.mean(winning_trades) if winning_trades else 0.0
        avg_loss = statistics.mean(losing_trades) if losing_trades else 0.0

        # Total fees paid
        total_fees = sum(t.fee for t in trades)

        return {
            "total_trades": len(trades),
            "buy_count": len(buy_trades),
            "sell_count": len(sell_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "avg_win": avg_win,
            "avg_loss": avg_loss,
            "total_fees": total_fees,
        }

    def calculate_latency_stats(self):
        """Calculate latency statistics"""
        stats = self.latency_tracker.get_event_stats()
        if not stats:
            return {
                "avg_latency_ms": 0.0,
                "max_latency_ms": 0.0,
                "min_latency_ms": 0.0,
            }

        return {
            "total_events": stats["count"],
            "avg_latency_ms": stats["mean"],
            "median_latency_ms": stats["median"],
            "min_latency_ms": stats["min"],
            "max_latency_ms": stats["max"],
            "stdev_latency_ms": stats["stdev"],
            "p95_latency_ms": stats["p95"],
            "p99_latency_ms": stats["p99"],
        }

    def generate_report(self):
        """Generate comprehensive results report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "returns": self.calculate_returns(),
            "sharpe_ratio": self.calculate_sharpe_ratio(),
            "calmar_ratio": self.calculate_calmar_ratio(),
            "max_drawdown": self.calculate_max_drawdown(),
            "trade_stats": self.calculate_trade_stats(),
            "latency_stats": self.calculate_latency_stats(),
        }
        return report

    def save_report_json(self, filename="results_report.json"):
        """Save report to JSON file"""
        report = self.generate_report()

        # Convert numpy/special types for JSON serialization
        def convert(obj):
            if isinstance(obj, (int, float)):
                return obj
            return str(obj)

        with open(filename, "w") as f:
            json.dump(report, f, indent=2, default=convert)

        print(f"\nReport saved to {filename}")

    def print_report(self):
        """Print formatted report to console"""
        report = self.generate_report()

        print("\n" + "=" * 60)
        print("TRADING SIMULATION RESULTS REPORT")
        print("=" * 60)

        # Returns
        ret = report["returns"]
        print(f"\nPERFORMANCE METRICS:")
        print(f"  Initial Capital:      ${self.initial_capital:,.2f}")
        print(f"  Final Portfolio Value: ${ret['final_value']:,.2f}")
        print(f"  Total Return:         {ret['total_return_pct']:.2f}%")
        print(f"  Sharpe Ratio:         {report['sharpe_ratio']:.3f}")
        print(f"  Calmar Ratio:         {report['calmar_ratio']:.3f}")
        print(f"  Max Drawdown:         {report['max_drawdown']*100:.2f}%")

        # Trading Stats
        ts = report["trade_stats"]
        print(f"\nTRADING STATISTICS:")
        print(f"  Total Trades:         {ts['total_trades']}")
        print(f"  Buy Orders:           {ts['buy_count']}")
        print(f"  Sell Orders:          {ts['sell_count']}")
        print(f"  Winning Trades:       {ts['winning_trades']}")
        print(f"  Losing Trades:        {ts['losing_trades']}")
        print(f"  Win Rate:             {ts['win_rate']*100:.2f}%")
        print(f"  Profit Factor:        {ts['profit_factor']:.3f}")
        print(f"  Avg Win:              ${ts['avg_win']:.4f}")
        print(f"  Avg Loss:             ${ts['avg_loss']:.4f}")
        print(f"  Total Fees Paid:      ${ts['total_fees']:.2f}")

        # Latency Stats
        ls = report["latency_stats"]
        print(f"\nLATENCY STATISTICS:")
        print(f"  Total Events:         {ls['total_events']}")
        print(f"  Avg Latency:          {ls['avg_latency_ms']:.4f} ms")
        print(f"  Median Latency:       {ls['median_latency_ms']:.4f} ms")
        print(f"  StDev Latency:        {ls['stdev_latency_ms']:.4f} ms")
        print(f"  Min Latency:          {ls['min_latency_ms']:.4f} ms")
        print(f"  Max Latency:          {ls['max_latency_ms']:.4f} ms")
        print(f"  P95 Latency:          {ls['p95_latency_ms']:.4f} ms")
        print(f"  P99 Latency:          {ls['p99_latency_ms']:.4f} ms")

        print("\n" + "=" * 60)

        return report

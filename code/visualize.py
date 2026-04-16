import matplotlib.pyplot as plt
import pickle


def load_data():
    with open("equity.pkl", "rb") as f:
        equity = pickle.load(f)

    with open("debug.pkl", "rb") as f:
        debug = pickle.load(f)

    with open("metrics.pkl", "rb") as f:
        metrics = pickle.load(f)

    return equity, debug, metrics


def plot_all():
    equity, debug, metrics = load_data()

    # --- BASE TIMELINE ---
    x = [d["event_index"] for d in debug]
    prices = [d["price"] for d in debug]
    signals = [d["signal"] for d in debug]

    # --- TRADES ---
    trade_x = [m["event_index"] for m in metrics]
    trade_prices = [m["price"] for m in metrics]
    trade_sides = [m["side"] for m in metrics]

    buy_x = [trade_x[i] for i in range(len(trade_x)) if trade_sides[i] == "BUY"]
    buy_prices = [trade_prices[i] for i in range(len(trade_x)) if trade_sides[i] == "BUY"]

    sell_x = [trade_x[i] for i in range(len(trade_x)) if trade_sides[i] == "SELL"]
    sell_prices = [trade_prices[i] for i in range(len(trade_x)) if trade_sides[i] == "SELL"]

    # --- EQUITY (resampled to event timeline) ---
    max_index = max([m["event_index"] for m in metrics], default=0) if metrics else 0
    equity_series = [None] * max(len(x), max_index + 1)
    for i, m in enumerate(metrics):
        if m["event_index"] < len(equity_series):
            equity_series[m["event_index"]] = m["value"]

    # forward fill
    last_val = 0
    for i in range(len(equity_series)):
        if equity_series[i] is None:
            equity_series[i] = last_val
        else:
            last_val = equity_series[i]

    # =========================
    # 1. PRICE + TRADES
    # =========================
    plt.figure(figsize=(12, 4))
    plt.plot(x, prices, label="Price", linewidth=2, color='black')
    
    if buy_x:
        plt.scatter(buy_x, buy_prices, marker='^', s=100, color='green', 
                   label=f"BUY ({len(buy_x)})", zorder=5)
    if sell_x:
        plt.scatter(sell_x, sell_prices, marker='v', s=100, color='red', 
                   label=f"SELL ({len(sell_x)})", zorder=5)
    
    plt.title("Market Price + Trade Execution")
    plt.xlabel("Event Index")
    plt.ylabel("Price")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

    # =========================
    # 2. SIGNAL
    # =========================
    plt.figure(figsize=(12, 4))
    plt.plot(x, signals, linewidth=1)
    
    # Color background for positive/negative signals
    positive_signals = [s if s > 0 else None for s in signals]
    negative_signals = [s if s < 0 else None for s in signals]
    
    plt.fill_between(x, 0, positive_signals, alpha=0.3, color='green', label='Bullish')
    plt.fill_between(x, 0, negative_signals, alpha=0.3, color='red', label='Bearish')
    
    plt.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
    plt.axhline(y=0.06, color='green', linestyle='--', linewidth=1, alpha=0.5, label='Entry Threshold')
    plt.axhline(y=-0.06, color='red', linestyle='--', linewidth=1, alpha=0.5)
    
    plt.title("Signal Strength Over Time")
    plt.xlabel("Event Index")
    plt.ylabel("Signal Strength")
    plt.ylim(-1.5, 1.5)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

    # =========================
    # 3. EQUITY (FIXED)
    # =========================
    plt.figure(figsize=(12, 4))
    plt.plot(x, equity_series, linewidth=2, color='blue', label='Portfolio Value')
    plt.axhline(y=100000, color='green', linestyle='--', linewidth=1, 
               alpha=0.5, label='Initial Capital')
    plt.fill_between(x, 100000, equity_series, where=[e >= 100000 for e in equity_series],
                     alpha=0.2, color='green', label='Profit')
    plt.fill_between(x, 100000, equity_series, where=[e < 100000 for e in equity_series],
                     alpha=0.2, color='red', label='Loss')
    plt.title("Equity Curve (Portfolio Value Over Time)")
    plt.xlabel("Event Index")
    plt.ylabel("Portfolio Value ($)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    plot_all()
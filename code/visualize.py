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
    equity_series = [None] * len(x)
    for i, m in enumerate(metrics):
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
    plt.figure()
    plt.plot(x, prices, label="Price")
    plt.scatter(buy_x, buy_prices, marker='^', label="BUY")
    plt.scatter(sell_x, sell_prices, marker='v', label="SELL")
    plt.title("Market + Execution")
    plt.xlabel("Event Index")
    plt.legend()
    plt.grid()
    plt.show()

    # =========================
    # 2. SIGNAL
    # =========================
    plt.figure()
    plt.plot(x, signals)
    plt.title("Signal Strength Over Time")
    plt.xlabel("Event Index")
    plt.grid()
    plt.show()

    # =========================
    # 3. EQUITY (FIXED)
    # =========================
    plt.figure()
    plt.plot(x, equity_series)
    plt.title("Equity Curve (Aligned)")
    plt.xlabel("Event Index")
    plt.ylabel("Portfolio Value")
    plt.grid()
    plt.show()


if __name__ == "__main__":
    plot_all()
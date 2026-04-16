from replay import MarketReplay
from dispatcher import EventDispatcher
from logger import Logger
from signalModel import BaselineSignalModel
from strategy import PredictionStrategy
from orderManager import OrderManager
from executionEngine import ExecutionEngine
from portfolio import Portfolio
from latency import LatencyTracker
from orderbook import LimitOrderBook
from riskManager import RiskManager

import pickle
from pathlib import Path


def main():
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "data" / "sp500.csv"
    equity_path = base_dir / "equity.pkl"

    replay = MarketReplay(str(data_path))
    dispatcher = EventDispatcher()
    logger = Logger()
    signal_model = BaselineSignalModel()
    strategy = PredictionStrategy(signal_model)
    order_manager = OrderManager()
    portfolio = Portfolio()
    latency = LatencyTracker()
    orderbook = LimitOrderBook()
    execution_engine = ExecutionEngine(orderbook)
    risk_manager = RiskManager()

    debug_log = []
    event_index = 0  # 🔥 KEY FIX

    # preload events
    while replay.has_events():
        dispatcher.push(replay.next_event())

    processed = 0
    max_events = 50000
    last_price = 0

    while dispatcher.has_events() and processed < max_events:

        event = dispatcher.pop()
        latency.start_event()

        price = float(event.payload["price"])
        quantity = int(float(event.payload.get("quantity", 1)))
        last_price = price

        # =========================
        # MARKET UPDATE
        # =========================
        latency.start_stage("market_update")
        orderbook.update_market(price, quantity)
        latency.stop_stage("market_update")

        # =========================
        # QUEUED EXECUTION
        # =========================
        latency.start_stage("queued_execution")
        queued_fills = execution_engine.process_market()
        latency.stop_stage("queued_execution")

        latency.start_stage("portfolio_update")
        for fill in queued_fills:
            portfolio.update(fill, price, event_index)  
        latency.stop_stage("portfolio_update")

        # =========================
        # SIGNAL
        # =========================
        latency.start_stage("signal_generation")
        signal = strategy.on_market_update(event, portfolio)
        latency.stop_stage("signal_generation")

        # =========================
        # ORDER FLOW
        # =========================
        if signal:
            latency.start_stage("order_creation")
            order = order_manager.create_order(signal, event)
            latency.stop_stage("order_creation")

            latency.start_stage("risk_check")
            approved = risk_manager.approve(order, portfolio)
            latency.stop_stage("risk_check")

            if approved:
                latency.start_stage("order_execution")
                fills = execution_engine.execute(order)
                latency.stop_stage("order_execution")

                latency.start_stage("portfolio_update")
                for fill in fills:
                    portfolio.update(fill, price, event_index)  
                latency.stop_stage("portfolio_update")

        # =========================
        # DEBUG LOG 
        # =========================
        debug_log.append({
            "event_index": event_index,
            "timestamp": event.timestamp,
            "price": price,
            "signal": signal["strength"] if signal else 0,
            "position": portfolio.position
        })

        latency.stop_event()

        processed += 1
        event_index += 1  

    # =========================
    # OUTPUT
    # =========================
    latency.summary()
    portfolio.summary()

    print("\nFinal Portfolio Value:", portfolio.value(last_price))

    with open(equity_path, "wb") as f:
        pickle.dump(portfolio.history, f)

    with open("debug.pkl", "wb") as f:
        pickle.dump(debug_log, f)

    with open("metrics.pkl", "wb") as f:
        pickle.dump(portfolio.metrics, f)


if __name__ == "__main__":
    main()
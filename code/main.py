from replay import MarketReplay
from dispatcher import EventDispatcher
from logger import Logger
from strategy import SimpleStrategy
from orderManager import OrderManager
from executionEngine import ExecutionEngine
from portfolio import Portfolio
from latency import LatencyTracker
from orderbook import LimitOrderBook
from riskManager import RiskManager

import pickle


def main():

    replay = MarketReplay("data/sp500.csv")
    dispatcher = EventDispatcher()
    logger = Logger()
    strategy = SimpleStrategy()
    order_manager = OrderManager()
    portfolio = Portfolio()
    latency = LatencyTracker()
    orderbook = LimitOrderBook()
    execution_engine = ExecutionEngine(orderbook)
    risk_manager = RiskManager()

    while replay.has_events():
        dispatcher.push(replay.next_event())

    processed = 0
    max_events = 50000
    last_price = 0

    while dispatcher.has_events() and processed < max_events:

        event = dispatcher.pop()

        latency.start()

        # logger.log_event(event)  # optional

        price = float(event.payload["price"])
        quantity = int(float(event.payload.get("quantity", 1)))
        last_price = price

        # update market state
        orderbook.update_market(price, quantity)

        # queued orders can fill as fresh market liquidity arrives
        queued_fills = execution_engine.process_market()
        for fill in queued_fills:
            portfolio.update(fill, price)

        # strategy signal
        signal = strategy.on_market_update(event, portfolio)

        if signal:

            order = order_manager.create_order(signal, event)

            # risk check BEFORE execution
            if risk_manager.approve(order, portfolio):

                fills = execution_engine.execute(order)

                # update portfolio with fills
                for fill in fills:
                    portfolio.update(fill, price)

        latency.stop()
        processed += 1

    latency.summary()
    portfolio.summary()

    print("\nFinal Portfolio Value:", portfolio.value(last_price))
    
    with open("equity.pkl", "wb") as f:
        pickle.dump(portfolio.history, f)


if __name__ == "__main__":
    main()

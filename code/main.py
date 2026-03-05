from replay import MarketReplay
from dispatcher import EventDispatcher
from logger import Logger
from strategy import SimpleStrategy
from orderManager import OrderManager
from executionEngine import ExecutionEngine
from portfolio import Portfolio
from latency import LatencyTracker


def main():

    # Initialize system components
    replay = MarketReplay("data/sp500.csv")
    dispatcher = EventDispatcher()
    logger = Logger()
    strategy = SimpleStrategy()
    order_manager = OrderManager()
    execution_engine = ExecutionEngine()
    portfolio = Portfolio()
    latency = LatencyTracker()

    # Load events from replay into dispatcher
    while replay.has_events():
        event = replay.next_event()
        dispatcher.push(event)

    processed = 0
    max_events = 5000

    while dispatcher.has_events() and processed < max_events:
       
        event = dispatcher.pop()
        latency.start()
        logger.log_event(event)

        signal = strategy.on_market_update(event)

        if signal:

            print("Signal:", signal)

            order = order_manager.create_order(signal, event)

            fill = execution_engine.execute(order)

            portfolio.update(fill)
        latency.stop()
        processed += 1
    latency.summary()
    portfolio.summary()


if __name__ == "__main__":
    main()
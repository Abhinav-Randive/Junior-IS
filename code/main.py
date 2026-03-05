from replay import MarketReplay
from dispatcher import EventDispatcher
from logger import Logger
from strategy import SimpleStrategy
from orderManager import OrderManager
from executionEngine import ExecutionEngine
from portfolio import Portfolio


def main():

    replay = MarketReplay("data/sp500.csv")
    dispatcher = EventDispatcher()
    logger = Logger()
    strategy = SimpleStrategy()
    order_manager = OrderManager()
    execution_engine = ExecutionEngine()
    portfolio = Portfolio()

    while replay.has_events():
        event = replay.next_event()
        dispatcher.push(event)

    processed = 0
    max_events = 200

    while dispatcher.has_events() and processed < max_events:

        event = dispatcher.pop()

        logger.log_event(event)

        signal = strategy.on_market_update(event)

        if signal:

            print("Signal:", signal)

            order = order_manager.create_order(signal, event)

            fill = execution_engine.execute(order)

            portfolio.update(fill)

        processed += 1

    portfolio.summary()


if __name__ == "__main__":
    main()
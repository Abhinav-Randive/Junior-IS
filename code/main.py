from replay import MarketReplay
from dispatcher import EventDispatcher
from logger import Logger
from strategy import SimpleStrategy
from orderManager import OrderManager
from executionEngine import ExecutionEngine
from portfolio import Portfolio
from latency import LatencyTracker
from orderbook import LimitOrderBook

def main():

    # Initialize system components
    replay = MarketReplay("data/sp500.csv")
    dispatcher = EventDispatcher()
    logger = Logger()
    strategy = SimpleStrategy()
    order_manager = OrderManager()
    portfolio = Portfolio()
    latency = LatencyTracker()
    orderbook = LimitOrderBook()
    execution_engine = ExecutionEngine(orderbook)

    # Load events from replay into dispatcher
    while replay.has_events():
        event = replay.next_event()
        dispatcher.push(event)

    processed = 0
    max_events = 50000

    while dispatcher.has_events() and processed < max_events:

        event = dispatcher.pop()

        latency.start()
        #logger.log_event(event)
        price = float(event.payload["price"])
        orderbook.update_market(price)
        signal = strategy.on_market_update(event)

        if signal:

            order = order_manager.create_order(signal, event)

            fills = execution_engine.execute(order)

            for fill in fills:
                portfolio.update(fill)

    
    latency.summary()
    portfolio.summary()

    last_price = float(event.payload["price"])
    print("\nPortfolio Value:", portfolio.value(last_price))


if __name__ == "__main__":
    main()
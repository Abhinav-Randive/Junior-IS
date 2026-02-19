from replay import MarketReplay
from dispatcher import EventDispatcher
from logger import Logger


def main():
    replay = MarketReplay("data/sp500.csv")
    dispatcher = EventDispatcher()
    logger = Logger()

    # Load all replay events into dispatcher
    while replay.has_next():
        event = replay.next_event()
        dispatcher.push(event)

    # Process events
    while dispatcher.has_events():
        event = dispatcher.pop()
        logger.log_event(event)


if __name__ == "__main__":
    main()

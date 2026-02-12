from events import Event, EventType

class MarketReplay:
    def __init__(self, data):
        self.data = data
        self.current_index = 0

    def has_events(self):
        return self.current_index < len(self.data)
    
    def next_event(self):
        row = self.data[self.current_index]
        self.current_index += 1

        return Event(
            timestamp=row['timestamp'],
            event_type=EventType.MARKET_UPDATE,
            payload=row
        )
    
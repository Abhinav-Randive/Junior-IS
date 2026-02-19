import csv
from events import Event, EventType


class MarketReplay:
    def __init__(self, filepath):
        self.data = []
        self.current_index = 0
        self._load_csv(filepath)

    def _load_csv(self, filepath):
        with open(filepath) as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.data.append(row)

    def has_events(self):
        return self.current_index < len(self.data)

    def next_event(self):
        if not self.has_events():
            return None

        row = self.data[self.current_index]
        self.current_index += 1

        return Event(
            timestamp=int(row['timestamp']),
            event_type=EventType.MARKET_UPDATE,
            payload=row
        )

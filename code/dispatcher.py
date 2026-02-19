import heapq


class EventDispatcher:
    def __init__(self):
        self._queue = []

    def push(self, event):
        """
        Insert event into priority queue ordered by timestamp.
        """
        heapq.heappush(self._queue, (event.timestamp, event))

    def has_events(self):
        return len(self._queue) > 0

    def pop(self):
        """
        Return next event in chronological order.
        """
        _, event = heapq.heappop(self._queue)
        return event

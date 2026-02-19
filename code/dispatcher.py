import heapq


class EventDispatcher:
    def __init__(self):
        self._queue = []
        self._counter = 0  # tie-breaker

    def push(self, event):
        # Use counter to prevent Event comparison
        heapq.heappush(self._queue, (event.timestamp, self._counter, event))
        self._counter += 1

    def has_events(self):
        return len(self._queue) > 0

    def pop(self):
        _, _, event = heapq.heappop(self._queue)
        return event

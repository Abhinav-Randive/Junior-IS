import time

class Logger:
    def log_event(self, event):
        now = time.perf_counter_ns()
        print(f"[{now}] {event.event_type} | {event.timestamp} | {event.payload}")
        
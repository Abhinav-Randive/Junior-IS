import time


class LatencyTracker:

    def __init__(self):
        self.event_start_time = None
        self.event_latencies = []
        self.stage_start_times = {}
        self.stage_latencies = {}

    def start_event(self):
        self.event_start_time = time.perf_counter()

    def stop_event(self):
        if self.event_start_time is None:
            return

        end_time = time.perf_counter()
        latency = (end_time - self.event_start_time) * 1000  # ms
        self.event_latencies.append(latency)
        self.event_start_time = None

    def start_stage(self, stage_name):
        self.stage_start_times[stage_name] = time.perf_counter()

    def stop_stage(self, stage_name):
        start_time = self.stage_start_times.pop(stage_name, None)
        if start_time is None:
            return

        latency = (time.perf_counter() - start_time) * 1000  # ms
        self.stage_latencies.setdefault(stage_name, []).append(latency)

    def _print_stats(self, label, latencies):
        avg = sum(latencies) / len(latencies)
        max_latency = max(latencies)
        min_latency = min(latencies)

        print(f"{label} count:", len(latencies))
        print(f"{label} average:", round(avg, 4), "ms")
        print(f"{label} max:", round(max_latency, 4), "ms")
        print(f"{label} min:", round(min_latency, 4), "ms")

    def summary(self):

        if not self.event_latencies:
            print("No latency recorded")
            return

        print("\nLatency Summary")
        self._print_stats("Event", self.event_latencies)

        for stage_name in sorted(self.stage_latencies):
            print()
            self._print_stats(stage_name, self.stage_latencies[stage_name])

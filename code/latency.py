import time


class LatencyTracker:

    def __init__(self):
        self.start_time = None
        self.latencies = []

    def start(self):
        self.start_time = time.perf_counter()

    def stop(self):
        end_time = time.perf_counter()
        latency = (end_time - self.start_time) * 1000  # ms
        self.latencies.append(latency)

    def summary(self):

        if not self.latencies:
            print("No latency recorded")
            return

        avg = sum(self.latencies) / len(self.latencies)
        max_latency = max(self.latencies)
        min_latency = min(self.latencies)

        print("\nLatency Summary")
        print("Events processed:", len(self.latencies))
        print("Average latency:", round(avg, 4), "ms")
        print("Max latency:", round(max_latency, 4), "ms")
        print("Min latency:", round(min_latency, 4), "ms")
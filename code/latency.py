"""
LATENCY TRACKING AND INSTRUMENTATION
====================================
Core measurement tool for the thesis: "Architecture Tradeoffs in Low-Latency Algorithmic Trading"

This module measures end-to-end latency and per-stage latency through the entire
trading pipeline. High-precision timing using perf_counter() for nanosecond accuracy.

Key Design Decisions:
1. Per-stage measurement: Isolate latency contribution of each component
2. Percentile tracking (p50, p95, p99): Show latency distribution, not just mean
3. No allocation during timing: Avoid GC interruption during critical sections

Thesis Application:
By breaking down latency by stage, we can quantify:
- Signal generation latency (model complexity)
- Execution latency (infrastructure overhead)
- Risk checking latency (controls vs. speed tradeoff)
- Total latency impact on trading signal timing
"""

import time
import statistics


class LatencyTracker:
    """
    High-precision latency measurement for algorithmic trading pipeline.
    
    Tracks two levels of latency:
    1. Event latency: Total time to process one market event (end-to-end)
    2. Stage latency: Time spent in each component (market update, signal gen, etc.)
    
    Implementation uses time.perf_counter() for platform-independent high resolution.
    """

    def __init__(self):
        """Initialize latency tracking data structures."""
        self.event_start_time = None  # Start time of current event
        self.event_latencies = []  # List of all end-to-end latencies (in ms)
        self.stage_start_times = {}  # Temporary storage for stage start times
        self.stage_latencies = {}  # Dict mapping stage_name -> list of latencies

    def start_event(self):
        """Mark the beginning of event processing."""
        self.event_start_time = time.perf_counter()

    def stop_event(self):
        """
        Mark the end of event processing and record latency.
        
        Formula: Latency (ms) = (end_time - start_time) * 1000
        
        Latency is one of the KEY METRICS for thesis validation.
        Higher latency means trading signals arrive late to market.
        """
        if self.event_start_time is None:
            return

        end_time = time.perf_counter()
        latency = (end_time - self.event_start_time) * 1000  # Convert to milliseconds
        self.event_latencies.append(latency)
        self.event_start_time = None

    def start_stage(self, stage_name):
        """
        Mark the beginning of a pipeline stage.
        
        Stages: "market_update", "signal_generation", "order_creation", 
                "risk_check", "order_execution", "portfolio_update", etc.
        
        Args:
            stage_name: Unique identifier for the pipeline stage
        """
        self.stage_start_times[stage_name] = time.perf_counter()

    def stop_stage(self, stage_name):
        """
        Mark the end of a pipeline stage and record its latency.
        
        The difference between stage latencies shows which components
        are the bottlenecks in the trading pipeline.
        
        Args:
            stage_name: Must match the stage_name from corresponding start_stage()
        """
        start_time = self.stage_start_times.pop(stage_name, None)
        if start_time is None:
            return

        latency = (time.perf_counter() - start_time) * 1000  # Convert to milliseconds
        # Append to list of latencies for this stage (compute stats later)
        self.stage_latencies.setdefault(stage_name, []).append(latency)

    def _calculate_stats(self, latencies):
        """
        Calculate comprehensive latency statistics.
        
        This is crucial for understanding latency distribution:
        - Mean: Average latency (affected by outliers)
        - Median: Middle value (robust to outliers)
        - StDev: Variability (consistency of latency)
        - Percentiles: Tail behavior (worst-case latency)
        
        For trading: P95 and P99 are more important than mean!
        A single 50ms delay during critical signal can cost trades.
        
        Args:
            latencies: List of latency measurements (in ms)
            
        Returns:
            dict: Statistics dictionary with count, mean, median, percentiles, etc.
        """
        if not latencies:
            return None

        sorted_latencies = sorted(latencies)
        stats = {
            "count": len(latencies),  # Number of measurements
            "mean": statistics.mean(latencies),  # Average
            "median": statistics.median(latencies),  # 50th percentile
            "min": min(latencies),  # Best case
            "max": max(latencies),  # Worst case
            "stdev": statistics.stdev(latencies) if len(latencies) > 1 else 0.0,  # Variability
            "p50": sorted_latencies[int(len(sorted_latencies) * 0.50)],  # 50th percentile
            "p95": sorted_latencies[int(len(sorted_latencies) * 0.95)],  # 95th percentile - important!
            "p99": sorted_latencies[int(len(sorted_latencies) * 0.99)],  # 99th percentile - worst case
        }
        return stats

    def _print_stats(self, label, latencies):
        """
        Pretty-print latency statistics with clear formatting.
        
        Used in reports and console output to make latency data human-readable.
        
        Args:
            label: Name for this statistics group
            latencies: List of latency measurements
        """
        stats = self._calculate_stats(latencies)
        if not stats:
            print(f"{label}: No data")
            return

        print(f"{label}:")
        print(f"  Count:  {stats['count']}")
        print(f"  Mean:   {stats['mean']:.4f} ms")
        print(f"  Median: {stats['median']:.4f} ms")
        print(f"  StDev:  {stats['stdev']:.4f} ms")
        print(f"  Min:    {stats['min']:.4f} ms")
        print(f"  Max:    {stats['max']:.4f} ms")
        print(f"  P95:    {stats['p95']:.4f} ms")  # Tail latency - critical for trading
        print(f"  P99:    {stats['p99']:.4f} ms")  # Extreme tail - worst-case

    def get_event_stats(self):
        """Return end-to-end event latency statistics as dictionary."""
        return self._calculate_stats(self.event_latencies)

    def get_stage_stats(self, stage_name):
        """
        Return specific stage latency statistics as dictionary.
        
        Useful for programmatic access to latency metrics for comparison/optimization.
        
        Args:
            stage_name: Pipeline stage identifier
            
        Returns:
            dict: Statistics for that stage or None if stage not found
        """
        if stage_name not in self.stage_latencies:
            return None
        return self._calculate_stats(self.stage_latencies[stage_name])

    def summary(self):
        if not self.event_latencies:
            print("No latency recorded")
            return

        print("\n" + "=" * 60)
        print("LATENCY SUMMARY")
        print("=" * 60)
        self._print_stats("Event Latencies", self.event_latencies)

        if self.stage_latencies:
            print()
            for stage_name in sorted(self.stage_latencies):
                print()
                self._print_stats(f"Stage: {stage_name}", self.stage_latencies[stage_name])
        print("=" * 60)

    def add_latency_offset(self, offset_ms):
        """Add simulated latency offset to the last recorded event"""
        if self.event_latencies:
            self.event_latencies[-1] += offset_ms

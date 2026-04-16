"""
ALGORITHMIC TRADING SYSTEM - Main Execution Loop
================================================
"Architecture Tradeoffs in Low-Latency Algorithmic Trading"

This module orchestrates the entire trading simulation pipeline:
1. Loads historical market data and replays events in timestamp order
2. Updates the limit order book with market prices
3. Processes pending orders and executes fills
4. Generates trading signals using technical indicators
5. Creates and executes new orders with risk controls
6. Tracks latency at each stage of the pipeline
7. Records execution metrics and portfolio performance

Key Architecture Decisions:
- Event-driven design for accurate latency measurement
- Staged pipeline to isolate latency contribution of each component
- Deterministic order execution with queue-based matching
- Comprehensive latency instrumentation for thesis validation
"""

from replay import MarketReplay
from dispatcher import EventDispatcher
from logger import Logger
from signalModel import BaselineSignalModel
from strategy import PredictionStrategy
from orderManager import OrderManager
from executionEngine import ExecutionEngine
from portfolio import Portfolio
from latency import LatencyTracker
from orderbook import LimitOrderBook
from riskManager import RiskManager
from results import ResultsAnalyzer
from execution import ExecutionAnalyzer

import pickle
from pathlib import Path


def main():
    """
    Main execution loop for the algorithmic trading simulator.
    
    Process:
    1. Initialize all components (market data, strategy, execution engine, etc.)
    2. Load historical market events into event queue
    3. Process events sequentially with latency tracking at each stage:
       - Market data updates
       - Existing order execution
       - Signal generation from technical indicators
       - New order creation and execution
       - Risk checks and portfolio updates
    4. Generate comprehensive reports with trading metrics and latency analysis
    5. Persist results to disk for further analysis
    
    Returns:
        Implicit: Generates output files (results_report.json, pickle files)
    """
    # Initialize paths and core components
    base_dir = Path(__file__).resolve().parent
    data_path = base_dir / "data" / "sp500.csv"
    equity_path = base_dir / "equity.pkl"

    # Market Data and Event Processing
    replay = MarketReplay(str(data_path))  # Loads historical market data
    dispatcher = EventDispatcher()  # Priority queue for chronological event processing
    
    # Strategy Components
    logger = Logger()  # Logging utility
    signal_model = BaselineSignalModel()  # Multi-indicator technical analysis model
    strategy = PredictionStrategy(signal_model)  # Entry/exit logic based on signals
    
    # Execution Components
    order_manager = OrderManager()  # Creates orders from trading signals
    orderbook = LimitOrderBook()  # Market microstructure - tracks bid/ask prices
    execution_engine = ExecutionEngine(orderbook)  # Matches orders against market
    risk_manager = RiskManager()  # Position limits and risk controls
    
    # Portfolio and Metrics
    portfolio = Portfolio()  # Tracks positions, cash, and P&L
    latency = LatencyTracker()  # Records latency of each pipeline stage
    
    # State variables
    debug_log = []  # Records detailed trade-by-trade information
    event_index = 0  # Tracks which event we're processing

    # ============================================
    # PHASE 1: Load all historical market events
    # ============================================
    # Pre-load events to ensure chronological order is preserved
    # Events are sorted by timestamp in the EventDispatcher
    while replay.has_events():
        dispatcher.push(replay.next_event())

    # Processing limits and state
    processed = 0
    max_events = 50000  # Process up to 50k events for performance
    last_price = 0  # Track final market price for portfolio valuation

    # ============================================
    # PHASE 2: Event-Driven Processing Loop
    # ============================================
    # Each iteration represents processing one market event
    # Latency is measured at each pipeline stage to quantify architectural impact
    while dispatcher.has_events() and processed < max_events:

        # Process next market event
        event = dispatcher.pop()
        latency.start_event()  # Start measuring total event latency

        # Extract market data from event
        price = float(event.payload["price"])
        quantity = int(float(event.payload.get("quantity", 1)))
        last_price = price

        # ==========================================================
        # STAGE 1: MARKET UPDATE
        # ==========================================================
        # Update the limit order book with new market price and liquidity
        # This determines the bid-ask spread for upcoming executions
        # Latency impact: <0.1ms typically - very fast market data processing
        latency.start_stage("market_update")
        orderbook.update_market(price, quantity)
        latency.stop_stage("market_update")

        # ==========================================================
        # STAGE 2: PROCESS PENDING ORDERS
        # ==========================================================
        # Execute any orders that are queued and can be filled at current market
        # This represents orders from PREVIOUS signals that are still waiting
        # Latency impact: Depends on queue depth - can be significant bottleneck
        latency.start_stage("queued_execution")
        queued_fills = execution_engine.process_market()
        latency.stop_stage("queued_execution")

        # Update portfolio with any fills from pending orders
        latency.start_stage("portfolio_update")
        for fill in queued_fills:
            portfolio.update(fill, price, event_index)  
        latency.stop_stage("portfolio_update")

        # ==========================================================
        # STAGE 3: SIGNAL GENERATION
        # ==========================================================
        # Compute trading signal from technical indicators (SMA, RSI, MACD, etc.)
        # This is the "prediction" component of the thesis
        # Latency impact: Model complexity directly impacts decision latency
        # - More indicators = slower signal generation
        # - This is a key architectural tradeoff
        latency.start_stage("signal_generation")
        signal = strategy.on_market_update(event, portfolio)
        latency.stop_stage("signal_generation")

        # ==========================================================
        # STAGE 4: ORDER CREATION & EXECUTION
        # ==========================================================
        # If we have a signal, create and execute a new order
        if signal:
            # Create order object from signal with metadata
            latency.start_stage("order_creation")
            order = order_manager.create_order(signal, event)
            latency.stop_stage("order_creation")

            # Check position limits and risk thresholds
            # This is another architectural layer - risk management adds latency
            latency.start_stage("risk_check")
            approved = risk_manager.approve(order, portfolio, price)
            latency.stop_stage("risk_check")

            # Execute order if risk check passes
            if approved:
                latency.start_stage("order_execution")
                fills = execution_engine.execute(order)
                latency.stop_stage("order_execution")

                # Update portfolio with new fills
                latency.start_stage("portfolio_update")
                for fill in fills:
                    portfolio.update(fill, price, event_index)  
                latency.stop_stage("portfolio_update")

        # ==========================================================
        # DEBUG LOGGING
        # ==========================================================
        # Record detailed trace for post-analysis and debugging
        debug_log.append({
            "event_index": event_index,
            "timestamp": event.timestamp,
            "price": price,
            "signal": signal["strength"] if signal else 0,
            "position": portfolio.position
        })

        # Stop measuring event latency
        latency.stop_event()

        # Increment counters for next iteration
        processed += 1
        event_index += 1  

    # ============================================
    # PHASE 3: Generate Reports and Persist Data
    # ============================================
    
    # Print latency breakdown by pipeline stage
    # This shows which components contributed most to latency
    # Key for identifying optimization opportunities
    latency.summary()
    
    # Print portfolio summary (positions, cash, trade count)
    portfolio.summary()

    # Calculate final portfolio value at last market price
    print("\nFinal Portfolio Value:", portfolio.value(last_price))

    # Generate comprehensive trading results report
    # Includes: returns, Sharpe ratio, drawdown, win rate, trade metrics
    analyzer = ResultsAnalyzer(portfolio, latency, last_price, initial_capital=100000)
    analyzer.print_report()
    analyzer.save_report_json("results_report.json")

    # Analyze execution quality (slippage, fill rates, queue positions)
    exec_analyzer = ExecutionAnalyzer(portfolio, None)
    exec_analyzer.print_execution_report()

    # Persist results for further analysis and visualization
    # equity.pkl: Full portfolio value history for backtesting
    # debug.pkl: Detailed trade-by-trade information
    # metrics.pkl: Comprehensive execution metrics
    with open(equity_path, "wb") as f:
        pickle.dump(portfolio.history, f)

    with open("debug.pkl", "wb") as f:
        pickle.dump(debug_log, f)

    with open("metrics.pkl", "wb") as f:
        pickle.dump(portfolio.metrics, f)


if __name__ == "__main__":
    main()
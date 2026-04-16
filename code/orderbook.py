"""
LIMIT ORDER BOOK - Market Microstructure Simulator
===================================================
Simulates realistic market microstructure with:
- Bid-ask spread (0.02% of mid-price)
- Limited liquidity at each price level
- Queue position-based execution probability
- Deterministic matching based on order hash

Key Architectural Features:
1. Realistic spread: Prevents arbitrage of latency
2. Liquidity constraints: Limits how many shares can be filled
3. Queue position: Earlier orders fill first (queue jumping penalty)
4. Deterministic hashing: Reproducible execution (for testing)

This is the "Market Realism" layer that prevents trivial advantage.
Without these constraints, even slow strategies would make money.
With them, latency BECOMES THE DIFFERENTIATOR (thesis validation).
"""

from collections import deque
import hashlib

from fill import Fill


class LimitOrderBook:
    """
    Simulates a realistic limit order book with market microstructure effects.
    """

    def __init__(self):
        """Initialize empty buy and sell queues with no market data yet."""
        # Queue of pending buy orders (orders waiting to be executed)
        self.buy_queue = deque()
        # Queue of pending sell orders
        self.sell_queue = deque()

        # Best bid and ask prices (updated from market data)
        self.best_bid = None  # Highest price buyers are willing to pay
        self.best_ask = None  # Lowest price sellers are willing to accept
        
        # Available liquidity at best prices
        # Prevents unlimited fills (realistic market constraint)
        self.buy_liquidity = 0  # Shares available to buy at best_bid
        self.sell_liquidity = 0  # Shares available to sell at best_ask

    def update_market(self, price, quantity=1):
        """
        Update the order book with new market price and liquidity.
        
        Called on every market event to reflect current bid-ask spread and volume.
        
        Spread Calculation:
        - Spread = price * 0.0002 (20 basis points, realistic for liquid stocks)
        - Best bid = price - spread (what buyers will pay)
        - Best ask = price + spread (what sellers want)
        
        Args:
            price: Latest market price (mid-price)
            quantity: Volume associated with this price update
        """
        spread = price * 0.0002  # 20 bps spread - prevents arbitrage
        self.best_bid = price - spread
        self.best_ask = price + spread

        # Update liquidity based on volume
        # Larger trades mean deeper liquidity at current price
        traded_quantity = max(1, int(float(quantity)))
        self.buy_liquidity = max(1, traded_quantity // 2)  # 50% of volume available to buy
        self.sell_liquidity = max(1, traded_quantity - self.buy_liquidity)  # 50% to sell

    def submit_order(self, order):
        """
        Add a new order to the appropriate queue.
        
        Orders are queued and processed during process_orders() call.
        
        Args:
            order: Order object with side ("BUY" or "SELL")
        """
        if order.side == "BUY":
            self.buy_queue.append(order)
        else:
            self.sell_queue.append(order)

    def _score_order(self, order):
        """
        Generate a deterministic but pseudo-random score for the order.
        
        This score determines whether an order gets filled based on its
        position in the queue. Orders are filled probabilistically based
        on their queue position.
        
        The hash ensures deterministic results for reproducible backtesting.
        
        Returns:
            float: Score between 0.0 and 1.0
        """
        basis = (
            f"{order.order_id}:{order.timestamp}:{order.remaining_quantity}:"
            f"{self.best_bid}:{self.best_ask}"
        )
        digest = hashlib.sha256(basis.encode("ascii")).hexdigest()
        # Convert first 8 hex chars to int and normalize to 0-1
        return int(digest[:8], 16) / 0xFFFFFFFF

    def _crosses_market(self, order):
        """
        Check if an order crosses the spread (i.e., would execute immediately).
        
        BUY orders cross if their price >= ask (willing to pay ask price)
        SELL orders cross if their price <= bid (willing to sell at bid)
        
        Args:
            order: Order to check
            
        Returns:
            bool: True if order would execute in market
        """
        if order.side == "BUY":
            return self.best_ask is not None and order.price >= self.best_ask
        return self.best_bid is not None and order.price <= self.best_bid

    def _process_queue(self, queue, side, probability_model):
        """
        Process a queue of orders and fill what can execute.
        
        This is where the realistic market microstructure matters:
        1. Orders must cross the market to execute
        2. Limited liquidity available at each price
        3. Queue position creates partial fill and latency penalty
        
        The probability_model determines fill likelihood based on queue position.
        Earlier orders get higher fill probability (queue jumping penalty).
        
        Args:
            queue: Deque of orders to process
            side: "BUY" or "SELL" (side of quotes to match against)
            probability_model: Function(order, queue_position) -> fill_probability
            
        Returns:
            list: List of Fill objects for orders that got filled
        """
        fills = []

        # Determine the trade price and available liquidity
        if side == "BUY":
            trade_price = self.best_ask  # Buyers execute at ask price
            available_liquidity = self.sell_liquidity  # Available shares to buy
        else:
            trade_price = self.best_bid  # Sellers execute at bid price
            available_liquidity = self.buy_liquidity  # Available shares to sell

        queue_position = 0
        while queue and available_liquidity > 0:
            order = queue[0]

            # Check if order would execute
            if not self._crosses_market(order):
                break

            # Determine if this order gets filled (probabilistic queue position)
            fill_probability = probability_model(order, queue_position)
            if self._score_order(order) > fill_probability:
                break  # This order doesn't fill - blocks rest of queue

            # Partial fill if necessary
            fill_quantity = min(order.remaining_quantity, available_liquidity)
            fills.append(
                Fill(
                    side=order.side,
                    price=trade_price,
                    quantity=fill_quantity,
                    timestamp=order.timestamp,
                    order_id=order.order_id,
                )
            )

            # Update order and liquidity
            order.remaining_quantity -= fill_quantity
            available_liquidity -= fill_quantity

            # Remove fully filled orders from queue
            if order.remaining_quantity == 0:
                queue.popleft()
            else:
                break  # Partially filled order blocks others

            queue_position += 1

        # Update liquidity for next processing
        if side == "BUY":
            self.sell_liquidity = available_liquidity
        else:
            self.buy_liquidity = available_liquidity

        return fills

    def process_orders(self, probability_model):
        """
        Process all queued orders and return fills.
        
        Called once per market event to execute pending orders.
        
        Args:
            probability_model: Function(order, queue_position) -> fill_probability
            
        Returns:
            list: All Fill objects from both buy and sell queues
        """
        fills = []
        fills.extend(self._process_queue(self.buy_queue, "BUY", probability_model))
        fills.extend(self._process_queue(self.sell_queue, "SELL", probability_model))

        return fills

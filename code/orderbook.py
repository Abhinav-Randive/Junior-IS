from fill import Fill

def process_orders(self):

    fills = []

    while self.buy_queue and self.sell_queue:

        buy = self.buy_queue[0]
        sell = self.sell_queue[0]

        if buy.price >= sell.price:

            trade_price = (buy.price + sell.price) / 2

            fills.append(Fill("BUY", trade_price, buy.quantity, buy.timestamp))
            fills.append(Fill("SELL", trade_price, sell.quantity, sell.timestamp))

            self.buy_queue.popleft()
            self.sell_queue.popleft()

        else:
            break

    return fills
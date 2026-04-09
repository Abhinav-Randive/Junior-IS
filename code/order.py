from dataclasses import dataclass, field

@dataclass
class Order:
    side: str
    price: float
    quantity: int
    timestamp: int
    order_id: int = 0
    remaining_quantity: int = field(init=False)

    def __post_init__(self):
        self.remaining_quantity = self.quantity

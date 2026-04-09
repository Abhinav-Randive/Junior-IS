from dataclasses import dataclass

@dataclass
class Fill:
    side: str
    price: float
    quantity: int
    timestamp: int
    order_id: int = 0
    fee: float = 0.0

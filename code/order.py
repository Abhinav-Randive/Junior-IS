from dataclasses import dataclass

@dataclass
class Order:
    side: str
    price: float
    quantity: int
    timestamp: int
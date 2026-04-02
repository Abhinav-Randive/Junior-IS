from dataclasses import dataclass

@dataclass
class Fill:
    side: str
    price: float
    quantity: int
    timestamp: int
from dataclasses import dataclass
from enum import Enum, auto

class EventType(Enum):
    MARKET_UPDATE = auto()
    ORDER_SUBMIT = auto()
    ORDER_CANCEL = auto()
    ORDER_EXECUTE = auto()

@dataclass
class Event:
    timestamp: int          # nanoseconds or microseconds
    event_type: EventType
    payload: dict

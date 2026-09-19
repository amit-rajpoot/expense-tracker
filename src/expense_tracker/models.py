from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from enum import Enum


class Category(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    RENT = "rent"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    OTHER = "other"


@dataclass
class Expense:
    id: int
    amount: Decimal
    category: Category
    description: str
    date: date
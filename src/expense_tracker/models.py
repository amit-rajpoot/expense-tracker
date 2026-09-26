from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

# <------------ CATEGORY ENUM ------------>


class Category(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    RENT = "rent"
    UTILITIES = "utilities"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    OTHER = "other"


# <------------ EXPENSE MODEL ------------>


@dataclass
class Expense:
    id: int
    amount: Decimal
    category: Category
    description: str
    date: date
    currency: str = "INR"
    created_at: datetime | None = None

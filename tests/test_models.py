from datetime import UTC, date, datetime
from decimal import Decimal

from expense_tracker.models import Category, Expense

# <------------ EXPENSE CREATION TEST ------------>


def test_expense_creation():

    expense = Expense(
        id=1,
        amount=Decimal("250.50"),
        category=Category.FOOD,
        description="Lunch",
        date=date(2026, 9, 24),
    )

    assert expense.id == 1
    assert expense.amount == Decimal("250.50")
    assert expense.category == Category.FOOD
    assert expense.description == "Lunch"
    assert expense.date == date(2026, 9, 24)


# <------------ CATEGORY TEST ------------>


def test_category_values():

    assert Category.FOOD.value == "food"
    assert Category.TRANSPORT.value == "transport"
    assert Category.RENT.value == "rent"
    assert Category.UTILITIES.value == "utilities"
    assert Category.ENTERTAINMENT.value == "entertainment"
    assert Category.HEALTH.value == "health"
    assert Category.OTHER.value == "other"


# <------------ EXPENSE DEFAULT TEST ------------>


def test_expense_defaults():

    expense = Expense(
        id=1,
        amount=Decimal("100.00"),
        category=Category.FOOD,
        description="Tea",
        date=date(2026, 9, 24),
    )

    assert expense.currency == "INR"
    assert expense.created_at is None


# <------------ EXPENSE WITH CREATED AT TEST ------------>


def test_expense_created_at():

    created_at = datetime(2026, 9, 24, 10, 30, tzinfo=UTC)

    expense = Expense(
        id=1,
        amount=Decimal("500.00"),
        category=Category.FOOD,
        description="Dinner",
        date=date(2026, 9, 24),
        created_at=created_at,
    )

    assert expense.created_at == created_at

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from .errors import StorageError
from .models import Category, Expense

# <------------ DATA FILE ------------>

DATA_FILE = Path(__file__).resolve().parents[2] / "expenses.json"


# <------------ LOAD EXPENSES ------------>

def load_expenses() -> list[Expense]:

    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            raw_data = json.load(file)

    except json.JSONDecodeError:

        print("Invalid Json data")
        return []

    if isinstance(raw_data, list):
        expense_data = raw_data

    elif isinstance(raw_data, dict):
        expense_data = raw_data.get("expenses", [])

    else:

        print("Invalid expense data.")
        return []

    expenses = []

    for expense in expense_data:

        try:

            expenses.append(
                Expense(
                    id=expense.get("id"),
                    amount=Decimal(expense["amount"]),
                    category=Category(expense["category"]),
                    description=expense["description"],
                    date=date.fromisoformat(expense["date"]),
                    currency=expense.get("currency", "INR"),
                    created_at=(
                        datetime.fromisoformat(
                            expense["created_at"]
                        )
                        if expense.get("created_at")
                        else None
                    ),
                )
            )

        except (KeyError, ValueError, TypeError):
            print(
                "Invalid expense data found "
                "skipping expense."
            )

    return expenses


# <------------ GET NEXT ID ------------>

def get_next_id() -> int:

    if not DATA_FILE.exists():
        return 1

    try:

        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError) as error:

        raise StorageError(
            f"Unable to read expense data: {error}"
        )

    if isinstance(data, dict):
        return data.get("next_id", 1)

    return 1


# <------------ SAVE EXPENSES ------------>

def save_expense(expenses: list[Expense]) -> None:

    data = []

    for expense in expenses:

        data.append(
            {
                "id": expense.id,
                "amount": str(expense.amount),
                "category": expense.category.value,
                "description": expense.description,
                "date": expense.date.isoformat(),
                "currency": expense.currency,
                "created_at": (
                    expense.created_at.isoformat()
                    if expense.created_at
                    else None
                ),
            }
        )

    next_id = get_next_id()
    schema = {
        "version": 1,
        "next_id": next_id + 1,
        "expenses": data,
    }

    temp_file = DATA_FILE.with_suffix(".tmp")

    try:
        with temp_file.open("w", encoding="utf-8") as file:

            json.dump(schema,file,indent=4)

        temp_file.replace(DATA_FILE)

    except OSError as error:
        if temp_file.exists():
            temp_file.unlink()

        raise StorageError(
            f"Unable to save expenses: {error}"
        )
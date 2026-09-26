import csv
import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from .errors import StorageError
from .models import Category, Expense

# <------------ DATA FILE ------------>

DATA_FILE = Path(__file__).resolve().parents[2] / "expenses.json"

# <------------ LOAD helpers ------------>


def _read_json_data() -> list | dict:
    if not DATA_FILE.exists():
        return []

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)

    except json.JSONDecodeError:
        print("Invalid Json data")
        return []


def _get_expense_data(raw_data: list | dict) -> list:
    if isinstance(raw_data, list):
        return raw_data

    if isinstance(raw_data, dict):
        return raw_data.get("expenses", [])

    print("Invalid expense data.")
    return []


def _parse_expense(expense: dict) -> Expense | None:
    try:
        return Expense(
            id=expense.get("id"),
            amount=Decimal(expense["amount"]),
            category=Category(expense["category"]),
            description=expense["description"],
            date=date.fromisoformat(expense["date"]),
            currency=expense.get("currency", "INR"),
            created_at=(
                datetime.fromisoformat(expense["created_at"])
                if expense.get("created_at")
                else None
            ),
        )

    except (KeyError, ValueError, TypeError):
        print("Invalid expense data found skipping expense.")
        return None


# <------------ LOAD EXPENSES ------------>
def load_expenses() -> list[Expense]:
    raw_data = _read_json_data()
    expense_data = _get_expense_data(raw_data)

    expenses = []

    for expense in expense_data:
        parsed_expense = _parse_expense(expense)

        if parsed_expense:
            expenses.append(parsed_expense)

    return expenses


# <------------ GET NEXT ID ------------>


def get_next_id() -> int:

    if not DATA_FILE.exists():
        return 1

    try:
        with DATA_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

    except (json.JSONDecodeError, OSError) as error:
        raise StorageError(f"Unable to read expense data: {error}")

    if isinstance(data, dict):
        return data.get("next_id", 1)

    return 1


# <------------ SAVE helpers ------------>


def _expense_to_dict(expense: Expense) -> dict:
    return {
        "id": expense.id,
        "amount": str(expense.amount),
        "category": expense.category.value,
        "description": expense.description,
        "date": expense.date.isoformat(),
        "currency": expense.currency,
        "created_at": (expense.created_at.isoformat() if expense.created_at else None),
    }


def _build_storage_data(
    expenses: list[Expense],
) -> dict:
    data = [_expense_to_dict(expense) for expense in expenses]
    next_id = get_next_id()

    return {
        "version": 1,
        "next_id": next_id + 1,
        "expenses": data,
    }


def _write_storage_data(data: dict) -> None:
    temp_file = DATA_FILE.with_suffix(".tmp")

    try:
        with temp_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4)

        temp_file.replace(DATA_FILE)

    except OSError as error:
        if temp_file.exists():
            temp_file.unlink()

        raise StorageError(f"Unable to save expenses: {error}")


# <------------ SAVE EXPENSES ------------>


def save_expense(expenses: list[Expense]) -> None:
    data = _build_storage_data(expenses)
    _write_storage_data(data)


# <------------ CSV helpers ------------>


def _csv_headers() -> list[str]:
    return [
        "id",
        "amount",
        "category",
        "description",
        "date",
        "currency",
        "created_at",
    ]


def _expense_to_csv_row(expense: Expense) -> list:
    return [
        expense.id,
        f"{expense.amount:.2f}",
        expense.category.value,
        expense.description,
        expense.date,
        expense.currency,
        expense.created_at,
    ]


def _write_csv(
    expenses: list[Expense],
    filename: Path,
) -> None:
    with filename.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as file:
        writer = csv.writer(file)
        writer.writerow(_csv_headers())

        for expense in expenses:
            writer.writerow(_expense_to_csv_row(expense))


# <------------ EXPORT CSV------------>


def export_expenses_to_csv(
    expenses: list[Expense],
    filename: Path,
) -> None:
    try:
        filename.parent.mkdir(
            parents=True,
            exist_ok=True,
        )
        _write_csv(expenses, filename)

    except OSError as error:
        raise StorageError(f"Unable to export file: {error}")

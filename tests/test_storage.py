import json
from datetime import date
from decimal import Decimal

from expense_tracker import storage
from expense_tracker.models import Category, Expense

# <------------ SAVE AND LOAD TEST ------------>


def test_save_and_load_expense(tmp_path, monkeypatch):
    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        storage,
        "DATA_FILE",
        test_file,
    )

    expense = Expense(
        id=1,
        amount=Decimal("250.50"),
        category=Category.FOOD,
        description="Lunch",
        date=date(2026, 9, 24),
    )

    storage.save_expense([expense])

    assert test_file.exists()

    expenses = storage.load_expenses()

    assert len(expenses) == 1
    assert expenses[0].id == 1
    assert expenses[0].amount == Decimal("250.50")
    assert expenses[0].category == Category.FOOD
    assert expenses[0].description == "Lunch"


# <------------ NEXT ID TEST ------------>


def test_get_next_id(tmp_path, monkeypatch):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        storage,
        "DATA_FILE",
        test_file,
    )

    assert storage.get_next_id() == 1

    data = {
        "version": 1,
        "next_id": 5,
        "expenses": [],
    }

    test_file.write_text(
        json.dumps(data),
        encoding="utf-8",
    )

    assert storage.get_next_id() == 5


# <------------ INVALID JSON TEST ------------>


def test_load_expenses_with_invalid_json(
    tmp_path,
    monkeypatch,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        storage,
        "DATA_FILE",
        test_file,
    )

    test_file.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    expenses = storage.load_expenses()

    assert expenses == []


# <------------ MISSING FILE TEST ------------>


def test_load_expenses_when_file_missing(
    tmp_path,
    monkeypatch,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        storage,
        "DATA_FILE",
        test_file,
    )

    expenses = storage.load_expenses()

    assert expenses == []

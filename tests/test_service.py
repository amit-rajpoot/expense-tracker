from decimal import Decimal

import pytest

from expense_tracker import service
from expense_tracker.models import Category

# <------------ ADD EXPENSE TEST ------------>


def test_add_expense(tmp_path, monkeypatch, capsys):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "250.50",
        "food",
        "Lunch",
        "2026-09-24",
    )

    captured = capsys.readouterr()

    assert "Expense added successfully!" in captured.out

    expenses = service.storage.load_expenses()

    assert len(expenses) == 1
    assert expenses[0].amount == Decimal("250.50")
    assert expenses[0].category == Category.FOOD


# <------------ INVALID AMOUNT TEST ------------>


def test_add_expense_invalid_amount():

    with pytest.raises(service.ValidationError):
        service.add_expense(
            "banana",
            "food",
            "Lunch",
            "2026-09-24",
        )


# <------------ NEGATIVE AMOUNT TEST ------------>


def test_add_expense_negative_amount():

    with pytest.raises(service.ValidationError):
        service.add_expense(
            "-100",
            "food",
            "Lunch",
            "2026-09-24",
        )


# <------------ INVALID DATE TEST ------------>


def test_add_expense_invalid_date():

    with pytest.raises(service.ValidationError):
        service.add_expense(
            "100",
            "food",
            "Lunch",
            "wrong-date",
        )


# <------------ FUTURE DATE TEST ------------>


def test_add_expense_future_date():

    with pytest.raises(service.ValidationError):
        service.add_expense(
            "100",
            "food",
            "Lunch",
            "2099-01-01",
        )


# <------------ INVALID CATEGORY TEST ------------>


def test_add_expense_invalid_category():

    with pytest.raises(service.ValidationError):
        service.add_expense(
            "100",
            "invalid-category",
            "Lunch",
            "2026-09-24",
        )


# <------------ EMPTY DESCRIPTION TEST ------------>


def test_add_expense_empty_description():

    with pytest.raises(service.ValidationError):
        service.add_expense(
            "100",
            "food",
            "",
            "2026-09-24",
        )


# <------------ LONG DESCRIPTION TEST ------------>


def test_add_expense_long_description():

    description = "a" * 101

    with pytest.raises(service.ValidationError):
        service.add_expense(
            "100",
            "food",
            description,
            "2026-09-24",
        )


# <------------ LIST EXPENSES TEST ------------>


def test_list_expenses(
    tmp_path,
    monkeypatch,
    capsys,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "250",
        "food",
        "Lunch",
        "2026-09-24",
    )

    service.list_expenses()

    captured = capsys.readouterr()

    assert "Lunch" in captured.out
    assert "250.00" in captured.out


# <------------ CATEGORY FILTER TEST ------------>


def test_list_category_filter(
    tmp_path,
    monkeypatch,
    capsys,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "250",
        "food",
        "Lunch",
        "2026-09-24",
    )

    service.add_expense(
        "100",
        "transport",
        "Bus",
        "2026-09-24",
    )

    service.list_expenses(category="food")

    captured = capsys.readouterr()

    assert "Lunch" in captured.out
    assert "Bus" not in captured.out


# <------------ DATE FILTER TEST ------------>


def test_list_date_filter(
    tmp_path,
    monkeypatch,
    capsys,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "100",
        "food",
        "Old Lunch",
        "2026-09-01",
    )

    service.add_expense(
        "200",
        "food",
        "New Lunch",
        "2026-09-24",
    )

    service.list_expenses(
        from_date="2026-09-20",
    )

    captured = capsys.readouterr()

    assert "New Lunch" in captured.out
    assert "Old Lunch" not in captured.out


# <------------ LIMIT TEST ------------>


def test_list_limit(
    tmp_path,
    monkeypatch,
    capsys,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    for number in range(5):
        service.add_expense(
            str(number + 1),
            "food",
            f"Expense {number}",
            "2026-09-24",
        )

    service.list_expenses(limit=2)

    captured = capsys.readouterr()

    assert captured.out.count("ID:") == 2


# <------------ SORT BY AMOUNT TEST ------------>


def test_list_sort_by_amount(
    tmp_path,
    monkeypatch,
    capsys,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "100",
        "food",
        "Small",
        "2026-09-24",
    )

    service.add_expense(
        "500",
        "food",
        "Large",
        "2026-09-24",
    )

    service.list_expenses(sort="amount")

    captured = capsys.readouterr()

    assert captured.out.index("Large") < captured.out.index("Small")


# <------------ DELETE SUCCESS TEST ------------>


def test_delete_expense(
    tmp_path,
    monkeypatch,
    capsys,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "250",
        "food",
        "Lunch",
        "2026-09-24",
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "y",
    )

    service.delete_expense(1)

    expenses = service.storage.load_expenses()

    assert expenses == []


# <------------ DELETE CANCEL TEST ------------>


def test_delete_cancelled(
    tmp_path,
    monkeypatch,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "250",
        "food",
        "Lunch",
        "2026-09-24",
    )

    monkeypatch.setattr(
        "builtins.input",
        lambda _: "n",
    )

    service.delete_expense(1)

    expenses = service.storage.load_expenses()

    assert len(expenses) == 1


# <------------ DELETE NOT FOUND TEST ------------>


def test_delete_not_found(
    tmp_path,
    monkeypatch,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    with pytest.raises(service.ValidationError):
        service.delete_expense(999)


# <------------ REPORT TEST ------------>


def test_expense_report(
    tmp_path,
    monkeypatch,
    capsys,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "250",
        "food",
        "Lunch",
        "2026-09-24",
    )

    service.add_expense(
        "100",
        "transport",
        "Bus",
        "2026-09-24",
    )

    service.expense_report()

    captured = capsys.readouterr()

    assert "food: ₹250.00" in captured.out
    assert "transport: ₹100.00" in captured.out
    assert "₹350.00" in captured.out


# <------------ REPORT MONTH FILTER TEST ------------>


def test_expense_report_month_filter(
    tmp_path,
    monkeypatch,
    capsys,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "250",
        "food",
        "September Lunch",
        "2026-09-24",
    )

    service.add_expense(
        "500",
        "food",
        "August Lunch",
        "2026-08-01",
    )

    service.expense_report(
        month="2026-09",
    )

    captured = capsys.readouterr()

    assert "250.00" in captured.out

    assert "500.00" not in captured.out


# <------------ INVALID MONTH TEST ------------>


def test_expense_report_invalid_month():

    with pytest.raises(service.ValidationError):
        service.expense_report(
            month="wrong-month",
        )


# <------------ INVALID YEAR TEST ------------>


def test_expense_report_invalid_year():

    with pytest.raises(service.ValidationError):
        service.expense_report(
            year=0,
        )


# <------------ EXPORT TEST ------------>


def test_export_expense(
    tmp_path,
    monkeypatch,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    service.add_expense(
        "250",
        "food",
        "Lunch",
        "2026-09-24",
    )

    output_file = tmp_path / "expenses.csv"

    service.export_expense(
        str(output_file),
    )

    assert output_file.exists()

    content = output_file.read_text(
        encoding="utf-8",
    )

    assert "Lunch" in content
    assert "250.00" in content


# <------------ EMPTY FILENAME TEST ------------>


def test_export_empty_filename(
    tmp_path,
    monkeypatch,
):

    test_file = tmp_path / "expenses.json"

    monkeypatch.setattr(
        service.storage,
        "DATA_FILE",
        test_file,
    )

    with pytest.raises(service.ValidationError):
        service.export_expense("")

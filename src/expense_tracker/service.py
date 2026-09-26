from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import storage
from .errors import ValidationError
from .models import Category, Expense

# <------------ ADD EXPENSE helpers ------------>


def _validate_amount(amount: str) -> Decimal:
    try:
        value = Decimal(amount)
    except InvalidOperation:
        raise ValidationError("Invalid amount.")

    if value <= 0:
        raise ValidationError("Amount must be greater than zero.")

    return value


def _validate_date(expense_date: str) -> date:
    try:
        parsed_date = date.fromisoformat(expense_date)
    except ValueError:
        raise ValidationError("Invalid date. Use YYYY-MM-DD format.")

    if parsed_date.isoformat() != expense_date:
        raise ValidationError("Invalid date. Use YYYY-MM-DD format.")

    if parsed_date > datetime.now().astimezone().date():
        raise ValidationError("Expense date cannot be in the Future.")

    return parsed_date


def _validate_category(category: str) -> Category:
    try:
        return Category(category.lower())
    except ValueError:
        allowed = ", ".join(item.value for item in Category)
        raise ValidationError(f"Invalid category. Allowed categories: {allowed}")


def _validate_description(description: str) -> str:
    description = description.strip()

    if not description:
        raise ValidationError("Description cannot be empty.")

    if len(description) > 100:
        raise ValidationError("Description can be 100 characters or less.")

    return description


def _create_expense(
    amount: Decimal,
    category: Category,
    description: str,
    expense_date: date,
) -> Expense:
    return Expense(
        id=storage.get_next_id(),
        amount=amount,
        category=category,
        description=description,
        date=expense_date,
        created_at=datetime.now().astimezone(),
    )


def _prepare_expense(
    amount: str,
    category: str,
    description: str,
    expense_date: str,
) -> Expense:
    return _create_expense(
        _validate_amount(amount),
        _validate_category(category),
        _validate_description(description),
        _validate_date(expense_date),
    )


# <------------ ADD EXPENSE ------------>


def add_expense(
    amount: str,
    category: str,
    description: str,
    expense_date: str,
) -> None:
    expense = _prepare_expense(
        amount,
        category,
        description,
        expense_date,
    )

    expenses = storage.load_expenses()
    expenses.append(expense)
    storage.save_expense(expenses)

    print("Expense added successfully!")


# <------------ LIST EXPENSES helpers ------------>


def _validate_list_category(category: str | None) -> str | None:
    if not category:
        return None

    try:
        Category(category.lower())
    except ValueError:
        allowed = ", ".join(item.value for item in Category)
        raise ValidationError(f"Invalid category. Allowed categories: {allowed}")

    return category


def _validate_list_filters(
    category: str | None,
    from_date: str | None,
    to_date: str | None,
    limit: int | None,
    sort: str,
) -> tuple[str | None, date | None, date | None]:
    category = _validate_list_category(category)

    parsed_from = _validate_date(from_date) if from_date else None
    parsed_to = _validate_date(to_date) if to_date else None

    if parsed_from and parsed_to and parsed_from > parsed_to:
        raise ValidationError("From date cannot be after To date.")

    if limit is not None and limit <= 0:
        raise ValidationError("Limit must be greater than zero.")

    if sort not in {"date", "amount"}:
        raise ValidationError("Invalid sort. Use date or amount.")

    return category, parsed_from, parsed_to


def _matches_expense(
    expense: Expense,
    category: str | None,
    from_date: date | None,
    to_date: date | None,
) -> bool:
    if category and expense.category.value != category:
        return False

    if from_date and expense.date < from_date:
        return False

    return not (to_date and expense.date > to_date)


def _filter_expenses(
    expenses: list[Expense],
    category: str | None,
    from_date: date | None,
    to_date: date | None,
) -> list[Expense]:
    return [
        expense
        for expense in expenses
        if _matches_expense(
            expense,
            category,
            from_date,
            to_date,
        )
    ]


def _sort_and_limit_expenses(
    expenses: list[Expense],
    sort: str,
    limit: int | None,
) -> list[Expense]:
    key = lambda expense: expense.amount if sort == "amount" else expense.date

    expenses.sort(key=key, reverse=True)

    return expenses[:limit] if limit is not None else expenses


def _display_expenses(
    expenses: list[Expense],
) -> None:
    if not expenses:
        print("No expenses found.")
        return

    for expense in expenses:
        print(f"ID: {expense.id}")
        print(f"Amount: ₹{expense.amount:.2f}")
        print(f"Category: {expense.category.value}")
        print(f"Description: {expense.description}")
        print(f"Date: {expense.date}")
        print()


# <------------ LIST EXPENSES ------------>


def list_expenses(
    category: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    limit: int | None = None,
    sort: str = "date",
) -> None:
    category, from_date, to_date = _validate_list_filters(
        category, from_date, to_date, limit, sort
    )
    expenses = _filter_expenses(
        storage.load_expenses(),
        category,
        from_date,
        to_date,
    )
    expenses = _sort_and_limit_expenses(expenses, sort, limit)
    _display_expenses(expenses)


# <------------ DELETE EXPENSE helpers ------------>


def _find_expense(
    expenses: list[Expense],
    expense_id: int,
) -> Expense:
    for expense in expenses:
        if expense.id == expense_id:
            return expense

    raise ValidationError(f"Expense with ID {expense_id} not found.")


def _confirm_delete(expense_id: int) -> bool:
    confirmation = input(f"Delete expense ID {expense_id}? (y/n): ").strip().lower()

    return confirmation == "y"


# <------------ DELETE EXPENSE ------------>


def delete_expense(expense_id: int) -> None:
    expenses = storage.load_expenses()
    expense = _find_expense(expenses, expense_id)

    if not _confirm_delete(expense_id):
        print("Delete cancelled.")
        return

    expenses.remove(expense)
    storage.save_expense(expenses)

    print("Expense Deleted successfully!")


# <------------ EXPENSE REPORT helpers ------------>


def _validate_report_filters(
    month: str | None,
    year: int | None,
) -> None:
    if month:
        try:
            date.fromisoformat(month + "-01")
        except ValueError:
            raise ValidationError("Invalid month. Use YYYY-MM format.")

    if year is not None and (year < 1 or year > 9999):
        raise ValidationError("Invalid year.")


def _filter_report_expenses(
    expenses: list[Expense],
    month: str | None,
    year: int | None,
) -> list[Expense]:
    return [
        expense
        for expense in expenses
        if (not month or expense.date.strftime("%Y-%m") == month)
        and (year is None or expense.date.year == year)
    ]


def _add_report_total(
    totals: dict[str, Decimal],
    key: str,
    amount: Decimal,
) -> None:
    totals[key] = (
        totals.get(
            key,
            Decimal(0),
        )
        + amount
    )


def _update_report_totals(
    expense: Expense,
    totals: dict[str, Decimal],
    monthly_totals: dict[str, Decimal],
) -> None:
    _add_report_total(
        totals,
        expense.category.value,
        expense.amount,
    )

    _add_report_total(
        monthly_totals,
        expense.date.strftime("%Y-%m"),
        expense.amount,
    )


def _calculate_report_totals(
    expenses: list[Expense],
) -> tuple[
    dict[str, Decimal],
    dict[str, Decimal],
    Decimal,
]:
    totals = {}
    monthly_totals = {}
    grand_total = Decimal(0)

    for expense in expenses:
        grand_total += expense.amount
        _update_report_totals(
            expense,
            totals,
            monthly_totals,
        )

    return totals, monthly_totals, grand_total


def _display_report(
    totals: dict[str, Decimal],
    monthly_totals: dict[str, Decimal],
    grand_total: Decimal,
) -> None:
    for category in sorted(totals):
        print(f"{category}: ₹{totals[category]:.2f}")

    print("\nMonthly Summary:")

    for expense_month in sorted(monthly_totals):
        print(f"{expense_month}: ₹{monthly_totals[expense_month]:.2f}")

    print("\nGrand Total:")
    print(f"₹{grand_total:.2f}")


# <------------ EXPENSE REPORT ------------>


def expense_report(
    month: str | None = None,
    year: int | None = None,
) -> None:
    _validate_report_filters(month, year)

    expenses = storage.load_expenses()

    if not expenses:
        print("No expense found.")
        return

    expenses = _filter_report_expenses(
        expenses,
        month,
        year,
    )

    if not expenses:
        print("No expenses found.")
        return

    report = _calculate_report_totals(expenses)
    _display_report(*report)


# <------------ EXPORT EXPENSES helpers ------------>


def _prepare_export_filename(filename: str) -> Path:
    filename = filename.strip()

    if not filename:
        raise ValidationError("Filename cannot be empty.")

    filename = Path(filename)

    if filename.suffix.lower() != ".csv":
        filename = filename.with_suffix(".csv")

    return filename


# <------------ EXPORT EXPENSES ------------>


def export_expense(filename: str) -> None:
    filename = _prepare_export_filename(filename)
    expenses = storage.load_expenses()

    if not expenses:
        print("No expenses to export.")
        return

    storage.export_expenses_to_csv(
        expenses,
        filename,
    )

    print(f"Expense exported to {filename}")

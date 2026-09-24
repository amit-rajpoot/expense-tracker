import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from . import storage 
from .errors import StorageError, ValidationError
from .models import Category, Expense

# <------------ ADD EXPENSE ------------>

def add_expense(amount,category,description,expense_date,):

    # ----------- AMOUNT VALIDATION ----------->

    try:
        amount = Decimal(amount)
        if not amount.is_finite():
            raise ValidationError("Invalid amount.")

        amount = amount.quantize(Decimal("0.01"))

    except (ValueError, InvalidOperation):

        raise ValidationError("Invalid amount.")

    # ----------- DATE VALIDATION ----------->

    try:
        expense_date = date.fromisoformat(expense_date)

    except ValueError:

        raise ValidationError(
            "Invalid date. Use YYYY-MM-DD format."
        )

    # ----------- CATEGORY VALIDATION ----------->

    category = category.lower()

    if category not in {
        item.value for item in Category
    }:

        allowed_categories = ", ".join(
            sorted(item.value for item in Category)
        )

        raise ValidationError(
            f"Invalid category. Allowed categories: "
            f"{allowed_categories}"
        )

    # ----------- DESCRIPTION VALIDATION ----------->

    if not description.strip():

        raise ValidationError(
            "Description cannot be empty."
        )
    
    if len(description.strip()) > 100:

        raise ValidationError(
            "Description can be 100 characters or less."
        )
    
    description = description.strip()

    # ----------- FUTURE DATE VALIDATION ----------->

    if expense_date > date.today():

        raise ValidationError(
            "Expense date cannot be in the Future."
        )

    # ----------- POSITIVE AMOUNT VALIDATION ----------->

    if amount <= 0:

        raise ValidationError(
            "Amount must be greater than zero."
        )

    # ----------- CREATE EXPENSE ----------->

    expenses = storage.load_expenses()

    expense = Expense(
        id=storage.get_next_id(),
        amount=amount,
        category=Category(category),
        description=description,
        date=expense_date,
        created_at=datetime.now(),
    )

    expenses.append(expense)

    storage.save_expense(expenses)

    print("Expense added successfully!")


# <------------ LIST EXPENSES ------------>

def list_expenses(category=None,from_date=None,to_date=None,limit=None,sort="date",):

    expenses = storage.load_expenses()

    # ----------- CATEGORY VALIDATION ----------->

    if category:
        category = category.lower()

    if category and category not in {
        item.value for item in Category
    }:

        allowed_categories = ", ".join(
            sorted(item.value for item in Category)
        )

        raise ValidationError(
            f"Invalid category. Allowed categories: "
            f"{allowed_categories}"
        )

    # ----------- SORT VALIDATION ----------->

    if sort not in {"date", "amount"}:

        raise ValidationError(
            "Invalid sort option. Use 'date' or 'amount'."
        )

    # ----------- DATE VALIDATION ----------->

    try:

        if from_date:
            from_date = date.fromisoformat(from_date)

        if to_date:
            to_date = date.fromisoformat(to_date)

    except ValueError:

        raise ValidationError(
            "Invalid date. Use YYYY-MM-DD format."
        )

    if from_date and to_date and from_date > to_date:

        raise ValidationError(
            "From date cannot be after to date."
        )

    # ----------- LIMIT VALIDATION ----------->

    if limit is not None and limit <= 0:

        raise ValidationError(
            "Limit must be greater than zero."
        )

    # ----------- FILTER EXPENSES ----------->

    filtered_expenses = []

    for expense in expenses:

        if category and expense.category.value != category:
            continue

        if from_date and expense.date < from_date:
            continue

        if to_date and expense.date > to_date:
            continue

        filtered_expenses.append(expense)

    # ----------- SORT EXPENSES ----------->

    if sort == "amount":

        filtered_expenses.sort(
            key=lambda expense: expense.amount,
            reverse=True,
        )

    else:

        filtered_expenses.sort(
            key=lambda expense: expense.date,
            reverse=True,
        )

    # ----------- APPLY LIMIT ----------->

    if limit:
        filtered_expenses = filtered_expenses[:limit]

    # ----------- NO EXPENSES ----------->

    if not filtered_expenses:

        print("No expenses found.")
        return

    # ----------- DISPLAY EXPENSES ----------->

    for expense in filtered_expenses:

        print(
            f"ID: {expense.id} | "
            f"{expense.date} | "
            f"{expense.category.value} | "
            f"₹{expense.amount:.2f} | "
            f"{expense.description} | "
            f"Created: {expense.created_at}"
        )


# <------------ DELETE EXPENSE ------------>

def delete_expense(expense_id):

    expenses = storage.load_expenses()

    for expense in expenses:

        if expense.id == expense_id:
            confirmation = input(
                f"Delete expense ID {expense_id}? (y/n): "
            ).strip().lower()

            if confirmation != "y":

                print("Delete cancelled.")
                return

            expenses.remove(expense)
            storage.save_expense(expenses)

            print("Expense Deleted successfully!")
            return

    raise ValidationError(
        f"Expense with ID {expense_id} not found."
    )


# <------------ EXPENSE REPORT ------------>

def expense_report(month=None,year=None,):

    expenses = storage.load_expenses()

    if not expenses:

        print("No expense found.")
        return

    # ----------- MONTH VALIDATION ----------->

    if month:

        try:

            date.fromisoformat(month + "-01")

        except ValueError:

            raise ValidationError(
                "Invalid month. Use YYYY-MM format."
            )

    # ----------- YEAR VALIDATION ----------->

    if year is not None and (
        year < 1 or year > 9999
    ):

        raise ValidationError("Invalid year.")

 
    totals = {}
    monthly_totals = {}
    grand_total = Decimal("0")

    # ----------- PROCESS EXPENSES ----------->

    for expense in expenses:
        expense_month = expense.date.strftime(
            "%Y-%m"
        )

        if month and expense_month != month:
            continue

        if year is not None and expense.date.year != year:
            continue

        category = expense.category.value
        amount = expense.amount

        grand_total += amount

        if category not in totals:
            totals[category] = Decimal("0")

        if expense_month not in monthly_totals:
            monthly_totals[expense_month] = Decimal("0")

        totals[category] += amount
        monthly_totals[expense_month] += amount

    # ----------- CATEGORY TOTAL ----------->

    if not totals:

        print("No expenses found.")
        return

    for category in sorted(totals):

        print(
            f"{category}: ₹{totals[category]:.2f}"
        )

    # ----------- MONTHLY SUMMARY ----------->

    print("\nMonthly Summary:")

    for expense_month in sorted(monthly_totals):

        print(
            f"{expense_month}: "
            f"₹{monthly_totals[expense_month]:.2f}"
        )

    # ----------- GRAND TOTAL ----------->

    print("\nGrand Total:")
    print(f"₹{grand_total:.2f}")


# <------------ EXPORT EXPENSES ------------>

def export_expense(filename):

    expenses = storage.load_expenses()
    filename = filename.strip()

    if not filename:

        raise ValidationError(
            "Filename cannot be empty."
        )

    filename = Path(filename)

    if filename.suffix.lower() != ".csv":

        filename = filename.with_suffix(".csv")

    if not expenses:

        print("No expenses to export.")
        return

    try:
        filename.parent.mkdir(parents=True,exist_ok=True,)

        with open(filename,"w",newline="",encoding="utf-8") as file:

            writer = csv.writer(file)
            writer.writerow(
                [
                    "id",
                    "amount",
                    "category",
                    "description",
                    "date",
                    "currency",
                    "created_at",
                ]
            )

            for expense in expenses:

                writer.writerow(
                    [
                        expense.id,
                        f"{expense.amount:.2f}",
                        expense.category.value,
                        expense.description,
                        expense.date,
                        expense.currency,
                        expense.created_at,
                    ]
                )

    except OSError as error:

        raise StorageError(
            f"Unable to export file: {error}"
        )

    print(f"Expense exported to {filename}")
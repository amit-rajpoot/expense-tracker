import csv
from datetime import date
from decimal import Decimal , InvalidOperation
from pathlib import Path

from .models import Expense, Category 
from .storage import load_expenses, save_expense

#-------""" ADD FUNCTION FOR EXPENSE """------>

def add_expense(amount, category, description, expense_date):

    #----------- AMOUNT VALIDATION ----------->
    
    try:
        amount = Decimal(amount)

        if not amount.is_finite():
           print("Invalid amount.")
           return


        amount = amount.quantize(Decimal("0.01"))
    except (ValueError,InvalidOperation):
        print("Invalid amount.")
        return
    #----------- DATE VALIDATION ----------->
    
    try:
        expense_date = date.fromisoformat(expense_date)
    except ValueError:
        print("Invalid date. Use YYYY-MM-DD format.")
        return


    #----------- CATEGORY VALIDATION ----------->

    category = category.lower()

    if category not in {item.value for item in Category}:
       print("Invalid category.")
       print(
         "Allowed categories:",
         ", ".join(sorted(item.value for item in Category))
       )
       return
    
    #----------- DESCRIPTION VALIDATION ----------->
    
    if not description.strip():
        print("Description cannot be empty.")
        return

    if not len(description.strip()) < 100:
        print("Description can be 100 characters or less.")
        return

    description = description.strip()
    #----------- FUTURE DATE VALIDATION ----------->
    
    if expense_date > date.today():
        print("Expense date cannot be in the Future.")
        return

    #----------- POSITIVE AMOUNT VALIDATION ----------->
    
    if amount <= 0:
        print("Amount must be greater than zero.")
        return
    #----------- CREATE EXPENSE ----------->
    expenses = load_expenses()

    expense = Expense(
        id = max(
            (expense.id or 0 for expense in expenses),
            default=0) + 1,
        amount = amount,
        category = Category(category),
        description =  description,
        date = expense_date

    )

    expenses.append(expense)
    save_expense(expenses)

    print("Expense added successfully!")

#-------""" Function for List expenses """------>
def list_expenses(category=None,from_date=None,to_date=None,limit=None,sort="date"):

    expenses = load_expenses()

    #----------- CATEGORY VALIDATION ----------->

    if category:
        category = category.lower()

    if category and category not in {item.value for item in Category}:
        print("Invalid category.")
        print(
            "Allowed categories:",
            ", ".join(sorted(item.value for item in Category))
        )
        return
    #----------- CHOICE VALIDATION ----------->
    if sort not in {"date" , "amount"}:
        print("Invalid sort option - Use 'date' or 'amount'")
        return

    #----------- DATE VALIDATION ----------->
    try:
        if from_date:
            from_date = date.fromisoformat(from_date)

        if to_date:
            to_date = date.fromisoformat(to_date)

    except ValueError:
        print("Invalid date! - Use YYYY-MM-DD format.")
        return

    if from_date and to_date and from_date > to_date:
        print("From date cannot be after to date.")
        return

    #----------- LIMIT VALIDATION ----------->

    if limit is not None and limit <= 0:
        print("Limit must be greater than zero.")
        return

    #----------- FILTER EXPENSES ----------->

    filtered_expenses = []

    for expense in expenses:

        if category and expense.category.value != category:
            continue

        if from_date and expense.date < from_date:
            continue

        if to_date and expense.date > to_date:
            continue

        filtered_expenses.append(expense)

    #----------- SORT EXPENSES ----------->

    if sort == "amount":

        filtered_expenses.sort(
            key=lambda expense: expense.amount,
            reverse=True
        )

    else:

        filtered_expenses.sort(
            key=lambda expense: expense.date,
            reverse=True
        )

    #----------- APPLY LIMIT ----------->

    if limit:
        filtered_expenses = filtered_expenses[:limit]

    #----------- NO EXPENSES ----------->

    if not filtered_expenses:
        print("No expenses found.")
        return

    #----------- DISPLAY EXPENSES ----------->

    for expense in filtered_expenses:

        print(
            f"ID: {expense.id} | "
            f"{expense.date} | "
            f"{expense.category.value} | "
            f"₹{expense.amount} | "
            f"{expense.description}"
        )


#-------""" Function for Delete expenses """------>

def delete_expense(expense_id):

    expenses = load_expenses()

    for expense in expenses:
        if expense.id == expense_id:

            confirmation = input(
                f"Delete expense ID {expense_id}? (y/n): "
            ).strip().lower()

            if confirmation != "y":
                print("Delete cancelled.")
                return
            
            expenses.remove(expense)
            save_expense(expenses)

            print("Expense Deleted successfully!")
            return
    print("Expense not found")

#-------""" Function for Report expenses """------>
def expense_report(month=None, year=None):

    expenses = load_expenses()

    if not expenses:
        print("No expense found.")
        return

    #----------- MONTH VALIDATION ----------->

    if month:
        try:
            date.fromisoformat(month + "-01")
        except ValueError:
            print("Invalid month. Use YYYY-MM format.")
            return

    #----------- YEAR VALIDATION ----------->

    if year is not None and (year < 1 or year > 9999):
        print("Invalid year.")
        return

    totals = {}
    monthly_totals = {}
    grand_total = Decimal("0")

    #----------- PROCESS EXPENSES ----------->

    for expense in expenses:

        expense_month = expense.date.strftime("%Y-%m")

        #----------- MONTH FILTER ----------->

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

    #----------- CATEGORY TOTAL ----------->

    if not totals:
        print("No expenses found.")
        return

    for category in sorted(totals):
        print(f"{category}:₹{totals[category]:.2f}")

    #----------- MONTHLY SUMMARY ----------->

    print("\nMonthly Summary:")

    for expense_month in sorted(monthly_totals):
        print(f"{expense_month}: ₹{monthly_totals[expense_month]:.2f}")

    #----------- GRAND TOTAL ----------->

    print("\nGrand Total:")
    print(f"₹{grand_total:.2f}")

#-------""" Function for Export expenses """------>
def export_expense(filename):

    expenses = load_expenses()

    filename = filename.strip()

    if not filename:
        print("Filename cannot be empty")
        return

    filename = Path(filename)

    if filename.suffix.lower() != ".csv":
        filename = filename.with_suffix(".csv")

    
    if not expenses:
        print("No expenses to export.")
        return

    try:
      # It create the directory if it doesn't exist
      filename.parent.mkdir(parents=True , exist_ok=True)

      with open(filename, "w", newline="", encoding="utf-8") as file:

        writer = csv.writer(file)

        writer.writerow([
            "id",
            "amount",
            "category",
            "description",
            "date"
        ])

        for expense in expenses:

            writer.writerow([
                expense.id,
                f"{expense.amount:.2f}",
                expense.category.value,
                expense.description,
                expense.date,
            ])

    except OSError:
      print("Unable to export file.")
      return

    print(f"Expense exported to {filename}")
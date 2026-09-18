import argparse
import json
from decimal import Decimal
from datetime import date
from pathlib import Path

VALID_CATEGORIES = {
    "food",
    "transport",
    "rent",
    "utilities",
    "entertainment",
    "health",
    "other"
}

#-------""" JSON PATH """------>

DATA_FILE = Path("expenses.json")

#-------""" Function for load json """------>
def load_expenses():
    if not DATA_FILE.exists():
        return []
    
    try:
        with DATA_FILE.open("r") as file:
         data = json.load(file)
    except json.JSONDecodeError:
        print("Invalid Json data.")
        return []

    expenses = []

    for expense in data:
        try:
            expenses.append({
            "amount":Decimal(expense["amount"]),
            "category":expense["category"],
            "description":expense["description"],
            "date":date.fromisoformat(expense["date"])
            })
        except (KeyError , ValueError):
            print("Invalid expense data found skipping expense.")
    return expenses

expenses = load_expenses()


#-------""" Function for save json """------>
def save_expense():

    data = []

    for expense in expenses:
        data.append({
            "amount":str(expense["amount"]),
            "category":expense["category"],
            "description":expense["description"],
            "date":expense["date"].isoformat()
        })


    with DATA_FILE.open("w") as file:
        json.dump(data, file, indent=4)


#-------""" ADD FUNCTION FOR EXPENSE """------>

def add_expense(amount, category, description, expense_date):

    #----------- AMOUNT VALIDATION ----------->
    
    try:
        amount = Decimal(amount)

        if not amount.is_finite():
           print("Invalid amount.")


        amount = amount.quantize(Decimal("0.01"))
    except ValueError:
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

    if category not in VALID_CATEGORIES:
        print("Invalid category.")
        print(
            "Allowed categories:",
            ", ".join(sorted(VALID_CATEGORIES))
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
    
    if expense_date > date.today():
        print("Expense date cannot be in the Future.")
        return

    if amount <= 0:
        print("Amount must be greater than zero.")
        return

    expense = {
        "amount": amount,
        "category": category,
        "description": description,
        "date": expense_date
    }

    expenses.append(expense)
    save_expense()

    print("Expense added successfully!")

#-------""" Function for List expenses """------>
def list_expenses(category=None,from_date=None,to_date=None,limit=None,sort="date"):

    #----------- CATEGORY VALIDATION ----------->

    if category:
        category = category.lower()

        if category not in VALID_CATEGORIES:
            print("Invalid category.")
            print(
                "Allowed categories:",
                ", ".join(sorted(VALID_CATEGORIES))
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

        if category and expense["category"] != category:
            continue

        if from_date and expense["date"] < from_date:
            continue

        if to_date and expense["date"] > to_date:
            continue

        filtered_expenses.append(expense)

    #----------- SORT EXPENSES ----------->

    if sort == "amount":

        filtered_expenses.sort(
            key=lambda expense: expense["amount"],
            reverse=True
        )

    else:

        filtered_expenses.sort(
            key=lambda expense: expense["date"],
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
            f"{expense['date']} | "
            f"{expense['category']} | "
            f"₹{expense['amount']} | "
            f"{expense['description']}"
        )

#-------""" Function for report expenses """------>
def expense_report(month=None, year=None):

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

        expense_month = expense["date"].strftime("%Y-%m")

        #----------- MONTH FILTER ----------->

        if month and expense_month != month:
            continue

        if year is not None and expense["date"].year != year:
            continue

        category = expense["category"]
        amount = expense["amount"]

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

#<------------ARGUMENT PARSER -------->

parser = argparse.ArgumentParser(
    description="A simple expense tracker CLI"
)


#----------- SUBPARSERS ----------->

subparsers = parser.add_subparsers(
    dest="command"
)


#--------------------ADD COMMAND--------->

add_parser = subparsers.add_parser("add")

add_parser.add_argument("amount")
add_parser.add_argument("category")
add_parser.add_argument("description")
add_parser.add_argument("date")


#---------------------LIST COMMAND --------->

list_parser = subparsers.add_parser("list")

list_parser.add_argument("--category")
list_parser.add_argument("--from-date")
list_parser.add_argument("--to-date")
list_parser.add_argument("--limit" , type=int)
list_parser.add_argument("--sort",choices=["date","amount"],default="date")


#------------------REPORT COMMAND ------------>

report_parser = subparsers.add_parser("report")

report_parser.add_argument("--month")
report_parser.add_argument("--year" , type=int)


#------- PARSE ARGUMENTS ---->

args = parser.parse_args()


if args.command == "add":

    add_expense(
        args.amount,
        args.category,
        args.description,
        args.date
    )

elif args.command == "list":
    
    list_expenses(args.category,
                  args.from_date,
                  args.to_date,
                  args.limit,
                  args.sort
    )

elif args.command == "report":
    expense_report(args.month,
                   args.year)
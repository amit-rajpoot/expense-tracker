import argparse
import json
from decimal import Decimal
from datetime import date
from pathlib import Path

#-------""" JSON PATH """------>

DATA_FILE = Path("expenses.json")

#-------""" Function for load json """------>
def load_expenses():
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r") as file:
        data = json.load(file)

    expenses = []

    for expense in data:
        expenses.append({
            "amount":Decimal(expense["amount"]),
            "category":expense["category"],
            "description":expense["description"],
            "date":date.fromisoformat(expense["date"])
        })
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

    amount = Decimal(amount)
    expense_date = date.fromisoformat(expense_date)
 
    if expense_date > date.today():
        print("Expense date cannot be in the Future")
        return

    if amount <= 0:
        print("Amount must be greater than zero")
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
def list_expenses(category=None , from_date=None , to_date=None):

    found = False 

    for expense in expenses:

        if category and expense["category"] != category:
            continue

        if from_date and expense["date"] < date.fromisoformat(from_date):
            continue

        if to_date and expense["date"] < date.fromisoformat(to_date):
            continue

        found = True

        print(
            f"{expense["date"]} | "
            f"{expense["category"]} | "
            f"{expense["amount"]} | "
            f"{expense["description"]} | "
        )

    if not found:
        print("No expense found")

#-------""" Function for report expenses """------>
def expense_report():

    totals = {}
    monthly_totals = {}

    for expense in expenses:

        category = expense["category"]
        month = expense["date"].strftime("%Y-%m")
        amount = expense["amount"]

        if category not in totals:
            totals[category] = Decimal("0")

        if month not in monthly_totals: 
            monthly_totals[month] = Decimal("0")


        totals[category] += amount
        monthly_totals[month] += amount

    for category ,total in totals.items():
        print(f"{category}:₹{total}")

    print("\nMonthly Summary:")
    
    for month , total in monthly_totals.items():
        print(f"{month} : ₹{total}")


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


#------------------REPORT COMMAND ------------>

report_parser = subparsers.add_parser("report")


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
                  args.to_date
    )

elif args.command == "report":
    expense_report()
import argparse
from decimal import Decimal

expenses = []


#-------""" ADD FUNCTION FOR EXPENSE """------>
def add_expense(amount, category, description):

    amount = Decimal(amount)

    if amount <= 0:
        print("Amount must be greater than zero")
        return

    expense = {
        "amount": amount,
        "category": category,
        "description": description
    }

    expenses.append(expense)

    print("Expense added successfully!")

    print(expenses) # Ye list of object return karega
    print(expense) # Ye bas item ko object table ke format mai return karega


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


#---------------------LIST COMMAND --------->

list_parser = subparsers.add_parser("list")


#------------------REPORT COMMAND ------------>

report_parser = subparsers.add_parser("report")


#------- PARSE ARGUMENTS ---->

args = parser.parse_args()
if args.command == "add":

    add_expense(
        args.amount,
        args.category,
        args.description
    )

elif args.command == "list":

    print("Listing expenses...")

elif args.command == "report":

    print("Generating report...")

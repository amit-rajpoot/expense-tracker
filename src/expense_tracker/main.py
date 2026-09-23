import argparse

from .service import (
    add_expense,
    list_expenses,
    delete_expense,
    expense_report,
    export_expense
)
from .errors import ValidationError , StorageError

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
list_parser.add_argument("--limit", type=int)
list_parser.add_argument(
    "--sort",
    choices=["date", "amount"],
    default="date"
)


#------------------REPORT COMMAND ------------>

report_parser = subparsers.add_parser("report")

report_parser.add_argument("--month")
report_parser.add_argument("--year", type=int)


#--------------------DELETE COMMAND--------->

delete_parser = subparsers.add_parser("delete")

delete_parser.add_argument("id", type=int)


#--------------------EXPORT COMMAND--------->

export_parser = subparsers.add_parser("export")

export_parser.add_argument(
    "filename",
    nargs="?",
    default="expenses.csv"
)


#------- MAIN FUNCTION ------>

def main():

    args = parser.parse_args()

    try:

     if args.command == "add":

        add_expense(
            args.amount,
            args.category,
            args.description,
            args.date
        )
 
     elif args.command == "list":

        list_expenses(
            args.category,
            args.from_date,
            args.to_date,
            args.limit,
            args.sort
        )

     elif args.command == "report":
 
        expense_report(
            args.month,
            args.year
        )

     elif args.command == "delete":

        delete_expense(args.id)

     elif args.command == "export":

        export_expense(args.filename)

    except (ValidationError, StorageError) as error:
       print(f"Error : {error}")

if __name__ == "__main__":
    main()
import argparse

from .errors import StorageError, ValidationError
from .service import (
    add_expense,
    delete_expense,
    expense_report,
    export_expense,
    list_expenses,
)

# <------------ ARGUMENT PARSER ------------>

parser = argparse.ArgumentParser(description="A simple expense tracker CLI")


# <------------ SUBPARSERS ------------>

subparsers = parser.add_subparsers(dest="command")


# <------------ ADD COMMAND ------------>

add_parser = subparsers.add_parser("add")

add_parser.add_argument("amount")
add_parser.add_argument("category")
add_parser.add_argument("description")
add_parser.add_argument("date")


# <------------ LIST COMMAND ------------>

list_parser = subparsers.add_parser("list")

list_parser.add_argument("--category")
list_parser.add_argument("--from-date")
list_parser.add_argument("--to-date")
list_parser.add_argument("--limit", type=int)

list_parser.add_argument(
    "--sort",
    choices=["date", "amount"],
    default="date",
)


# <------------ REPORT COMMAND ------------>

report_parser = subparsers.add_parser("report")

report_parser.add_argument("--month")
report_parser.add_argument("--year", type=int)


# <------------ DELETE COMMAND ------------>

delete_parser = subparsers.add_parser("delete")

delete_parser.add_argument("id", type=int)


# <------------ EXPORT COMMAND ------------>

export_parser = subparsers.add_parser("export")

export_parser.add_argument(
    "filename",
    nargs="?",
    default="expenses.csv",
)


# <------------ PARSE ARGUMENTS ------------>


def parse_args():

    return parser.parse_args()


# <------------ COMMAND HANDLERS ------------>


def _handle_add(args):
    add_expense(
        args.amount,
        args.category,
        args.description,
        args.date,
    )


def _handle_list(args):
    list_expenses(
        args.category,
        args.from_date,
        args.to_date,
        args.limit,
        args.sort,
    )


def _handle_report(args):
    expense_report(
        args.month,
        args.year,
    )


def _handle_delete(args):
    delete_expense(args.id)


def _handle_export(args):
    export_expense(args.filename)


# <------------ COMMAND DISPATCHER ------------>


def run():
    args = parse_args()

    handlers = {
        "add": _handle_add,
        "list": _handle_list,
        "report": _handle_report,
        "delete": _handle_delete,
        "export": _handle_export,
    }

    try:
        handler = handlers.get(args.command)

        if handler:
            handler(args)

    except (ValidationError, StorageError) as error:
        print(f"Error: {error}")

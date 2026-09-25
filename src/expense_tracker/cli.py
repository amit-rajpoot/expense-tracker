import argparse

# <------------ ARGUMENT PARSER ------------>

parser = argparse.ArgumentParser(
    description="A simple expense tracker CLI"
)


# <------------ SUBPARSERS ------------>

subparsers = parser.add_subparsers(
    dest="command"
)


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
from .cli import parse_args
from .errors import StorageError, ValidationError
from .service import (
    add_expense,
    delete_expense,
    expense_report,
    export_expense,
    list_expenses,
)


def main():

    args = parse_args()

    try:

        # <------------ ADD ------------>

        if args.command == "add":
            add_expense(
                args.amount,
                args.category,
                args.description,
                args.date,
            )

        # <------------ LIST ------------>

        elif args.command == "list":
            list_expenses(
                args.category,
                args.from_date,
                args.to_date,
                args.limit,
                args.sort,
            )

        # <------------ REPORT ------------>

        elif args.command == "report":
            expense_report(
                args.month,
                args.year,
            )

        # <------------ DELETE ------------>

        elif args.command == "delete":
            delete_expense(args.id)

        # <------------ EXPORT ------------>

        elif args.command == "export":
            export_expense(args.filename)

    # <------------ ERROR HANDLING ------------>

    except (ValidationError, StorageError) as error:
        print(f"Error: {error}")


# <------------ PROGRAM ENTRY POINT ------------>

if __name__ == "__main__":
    main()
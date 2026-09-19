import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from expense_tracker.models import Expense , Category


DATA_FILE = Path("expenses.json")


#-------""" Function for LOAD json """------>
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
            expenses.append(
                Expense(
                    id=expense.get("id"),
                    amount=Decimal(expense["amount"]),
                    category=Category(expense["category"]),
                    description=expense["description"],
                    date=date.fromisoformat(expense["date"])
                )
                
            )
        except (KeyError , ValueError):
            print("Invalid expense data found skipping expense.")
    return expenses

expenses = load_expenses()

#-------""" Function for save json """------>
def save_expense(expenses):

    data = []

    for expense in expenses:
        data.append({
            "id": expense.id,
            "amount":str(expense.amount),
            "category":expense.category.value,
            "description":expense.description,
            "date":expense.date.isoformat()
        })

    try:
        with DATA_FILE.open("w" , encoding="utf-8") as file:
          json.dump(data, file, indent=4)

    except OSError:
        print("Unable to save expenses.")

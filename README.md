# Expense Tracker CLI

A simple command-line expense tracker built with Python.

## Features

- Add expenses
- List expenses
- Filter expenses by category
- Filter expenses by date range
- Sort expenses by date or amount
- Generate expense reports
- Delete expenses
- Export expenses to CSV
- Persistent JSON storage
- Input validation
- Custom error handling
- Automated tests
- Ruff code-quality checks

## Tech Stack

- Python 3.12+
- argparse
- JSON
- CSV
- pytest
- Ruff
- uv

## Project Structure

```text
expense-tracker/
├── src/
│   └── expense_tracker/
│       ├── __init__.py
│       ├── cli.py
│       ├── errors.py
│       ├── main.py
│       ├── models.py
│       ├── service.py
│       └── storage.py
│
├── tests/
│   ├── test_models.py
│   ├── test_service.py
│   └── test_storage.py
│
├── expenses.json
├── README.md
├── pyproject.toml
└── uv.lock
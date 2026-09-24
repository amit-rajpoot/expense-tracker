# <------------ BASE ERROR ------------>
class ExpenseTrackerError(Exception):
    """Base exception for expense tracker."""


# <------------ VALIDATION ERROR ------------>
class ValidationError(ExpenseTrackerError):
    """Raised when user input is invalid."""


# <------------ STORAGE ERROR ------------>
class StorageError(ExpenseTrackerError):
    """Raised when storage operation fails."""
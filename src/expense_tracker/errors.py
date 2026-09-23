class ExpenseTrackerError(Exception):
    """Base exception for expense tracker."""
class ValidationError(Exception):
    """Raised when user input is invalid"""
class StorageError(Exception):
    """Raised when expense storage fails"""
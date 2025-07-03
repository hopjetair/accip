class DatabaseQueryError(Exception):
    """Raised when a database query fails."""
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.original_exception = original_exception

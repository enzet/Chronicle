class ChronicleException(Exception):
    """Chronicle error that should be handled."""

    def __init__(self, message: str):
        self.message = message


class ChronicleError(Exception):
    """Exception raised for errors in the value."""

    def __init__(self, message: str):
        self.message = message


class ChronicleAmbiguousArgumentError(ChronicleError):
    """Exception raised for ambiguous argument."""


class ChronicleArgumentError(ChronicleError):
    """Exception raised for argument errors."""


class ChronicleObjectNotFoundException(ChronicleException):
    """Exception raised for object not found."""

    def __init__(self, object_id: str) -> None:
        self.object_id = object_id


class ChronicleCodeException(ChronicleException):
    """Exception raised for code errors."""


class ChronicleValueException(ChronicleException):
    """Exception raised for value errors."""

"""Chronicle-specific errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from chronicle.event.core import Event
    from chronicle.value import Value


class ChronicleError(Exception):
    """Chronicle error that should be handled."""

    def __init__(self, message: str) -> None:
        self.message: str = message


class ChronicleSummaryError(ChronicleError):
    """There is no enough data in the timeline to create a summary."""

    def __init__(self, message: str, event: Event | None = None) -> None:
        super().__init__(message)
        self.event = event


class ChronicleArgumentError(ChronicleError):
    """Exception raised for argument errors."""


class ChronicleAmbiguousArgumentError(ChronicleArgumentError):
    """Exception raised for ambiguous argument."""


class ChronicleObjectNotFoundError(ChronicleError):
    """Exception raised for object not found."""

    def __init__(self, object_id: str) -> None:
        self.object_id = object_id


class ChronicleModelError(ChronicleError):
    """Internal error in Chronicle model."""


class ChronicleValueError(ChronicleError):
    """Exception raised for value errors."""

    def __init__(self, message: str, element: Value | None = None) -> None:
        super().__init__(message)
        self.element = element


class ChronicleUnknownTypeError(ChronicleValueError):
    """Exception raised for unknown type."""

    def __init__(self, message: str, type_: str) -> None:
        super().__init__(message)
        self.type_: str = type_


class ChronicleParseError(ChronicleValueError):
    """Exception raised for parse errors."""

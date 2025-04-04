import logging
from types import UnionType

from chronicle.event.art import Language  # noqa: F401
from chronicle.event.common import Cost  # noqa: F401

# Do not delete: these imports add classes to `globals`.
from chronicle.event.core import Event
from chronicle.time import Timedelta  # noqa: F401
from chronicle.value import ChronicleValueException  # noqa: F401
from chronicle.value import Interval  # noqa: F401


def construct_types(event_class: type[Event], field_: str) -> list:
    """Construct types for a field."""

    if field_ in ["from", "to"]:
        field_ += "_"

    if (
        "__dataclass_fields__" in event_class.__dict__
        and field_ in event_class.__dict__["__dataclass_fields__"]
    ):
        value_class = event_class.__dict__["__dataclass_fields__"][field_].type
    else:
        logging.error(
            "`%s` doesn't have `%s` field.", event_class.__name__, field_
        )
        return []

    if isinstance(value_class, UnionType):
        types = []
        for type_ in str(value_class).split(" | "):
            if "." in type_:
                type_ = type_.split(".")[-1]
            if type_ in globals():
                types.append(globals()[type_])
            elif type_ in __builtins__:
                types.append(__builtins__[type_])
            else:
                raise TypeError(type_, type(type_))

        return types

    return [value_class]


def fill(data: dict, class_: type[Event], object_: Event) -> None:
    """Fill object from data."""

    for key, value in data.items():
        if key in ["type", "time", "id"] or key.startswith("__"):
            continue
        for value_class in construct_types(class_, key):
            if value_class in [str, bool, float, int]:
                try:
                    object_.__setattr__(key, value_class(value))
                except TypeError:
                    logging.error(
                        "Cannot convert field `%s` with value `%s` (`%s`) to "
                        "`%s`.",
                        key,
                        value,
                        type(value).__name__,
                        value_class.__name__,
                    )
                except ValueError:
                    logging.error(
                        "Cannot convert field `%s` with value `%s` (`%s`) to "
                        "`%s`.",
                        key,
                        value,
                        type(value).__name__,
                        value_class.__name__,
                    )
                break
            else:
                try:
                    object_.__setattr__(key, value_class.from_json(value))
                except AttributeError:
                    logging.error(
                        "Cannot convert field `%s` with value `%s` (`%s`) to "
                        "`%s`.",
                        key,
                        value,
                        type(value).__name__,
                        value_class.__name__,
                    )
                break

import logging
from dataclasses import dataclass
from types import UnionType
from typing import Any

# Do not delete: these imports add classes to `globals`.
from chronicle.time import Timedelta  # noqa: F401
from chronicle.event.art import Language  # noqa: F401
from chronicle.value import ChronicleValueException  # noqa: F401
from chronicle.value import Interval  # noqa: F401
from chronicle.event.common import Cost  # noqa: F401


def construct_types(event_class, field_: str) -> list:
    if field_ in ["from", "to"]:
        field_ += "_"

    if (
        "__dataclass_fields__" in event_class.__dict__
        and field_ in event_class.__dict__["__dataclass_fields__"]
    ):
        value_class = event_class.__dict__["__dataclass_fields__"][field_].type
    else:
        logging.error(
            f"`{event_class.__name__}` doesn't have `{field_}` field."
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


def fill(data: dict, class_, object_):
    for key, value in data.items():
        if key in ["type", "time", "id"] or key.startswith("__"):
            continue
        for value_class in construct_types(class_, key):
            if value_class in [str, bool, float, int]:
                try:
                    object_.__setattr__(key, value_class(value))
                except TypeError:
                    logging.error(
                        f"Cannot convert field `{key}` with value "
                        f"`{value}` (`{type(value).__name__}`) to "
                        f"`{value_class.__name__}`."
                    )
                except ValueError:
                    logging.error(
                        f"Cannot convert field `{key}` with value "
                        f"`{value}` (`{type(value).__name__}`) to "
                        f"`{value_class.__name__}`."
                    )
                break
            else:
                try:
                    object_.__setattr__(key, value_class.from_json(value))
                except AttributeError:
                    logging.error(
                        f"Cannot convert field `{key}` with value "
                        f"`{value}` (`{type(value).__name__}`) to "
                        f"`{value_class.__name__}`."
                    )
                break


@dataclass
class Serializable:
    @classmethod
    def from_json(cls, data: Any) -> "Serializable":
        object_ = cls()
        if isinstance(data, dict):
            fill(data, cls, object_)
        else:
            # Should be implemented in subclass.
            raise NotImplementedError(
                f"`from_json` is not implemented for `{cls.__name__}`, type "
                f"is `{type(data)}`"
            )

        return object_

    def to_json(self) -> Any:
        raise NotImplementedError()

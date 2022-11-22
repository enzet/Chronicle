import re
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Argument:
    name: str
    description: str | None = None
    prefix: str | None = None
    pattern: re.Pattern | None = None
    loader: Callable[[Any], Any] = lambda x: x

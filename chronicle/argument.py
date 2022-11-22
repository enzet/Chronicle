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


class ArgumentParser:
    def __init__(self, prefixes: list[str]) -> None:
        self.prefixes: list[str] = prefixes
        self.arguments: list[Argument] = []

    def parse(self, text: str) -> dict[str, str] | None:

        main: Argument = self.arguments[0]
        result: dict[str, str] = {}
        words = text.split(" ")

        current: str = ""
        closed: bool = False

        for index in range(len(words)):

            word = words[index]
            for argument in self.arguments:

                if word == argument.prefix:
                    result[argument.name] = argument.loader(words[index + 1])
                    index += 1
                    closed = True
                    continue

                if argument.pattern and (
                    matcher := argument.pattern.match(word)
                ):
                    group_dict = matcher.groupdict()
                    if argument.loader is not None:
                        result[argument.name] = argument.loader(group_dict)
                    else:
                        for group_name, group_value in group_dict.items():
                            result[group_name] = group_value
                    closed = True
                    break

            if not closed:
                if not result[main.name]:
                    result[main.name] = main.loader(word)
                else:
                    result[main.name] += " " + word

        return result

    def add_argument(
        self,
        name: str,
        description: str | None = None,
        prefix: str | None = None,
        pattern: re.Pattern | None = None,
        loader: Callable = lambda x: x,
    ) -> "ArgumentParser":

        argument: Argument = Argument(
            name,
            description,
            prefix=prefix,
            pattern=pattern,
            loader=loader,
        )
        self.arguments.append(argument)
        return self

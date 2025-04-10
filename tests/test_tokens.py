"""Tests for tokens."""

from dataclasses import dataclass


@dataclass
class Token:
    """A token of a command."""

    value: str
    """Value of the token."""

    language: str | None = None
    """Language of the token."""


def parse_tokens(command: str) -> list[Token]:
    """Parse string command into tokens, splitting by spaces.

    Specially treat quoted text, like `"text"` and language-specific quotes,
    like `en"text"` or `fr"text"`, as well as quotation marks escaping.
    """
    parts: list[Token] = []
    current: str = ""
    current_language: str | None = None
    index: int = 0
    in_quotes: bool = False
    quote_char: str | None = None

    while index < len(command):
        char: str = command[index]

        # Handle language prefixes like en"text".
        if (
            not in_quotes
            and index + 2 < len(command)
            and command[index + 2] == '"'
            and command[index : index + 2].isalpha()
        ):
            current_language = command[index : index + 2]
            index += 2
            continue

        # Start of quote.
        if char == '"' and not in_quotes:
            if index > 0 and command[index - 1] == "\\":
                current = current[:-1] + char
                index += 1
                continue

            in_quotes = True
            quote_char = char
            index += 1
            continue

        # End of quote.
        if char == quote_char and in_quotes:
            if index > 0 and command[index - 1] == "\\":
                current = current[:-1] + char
                index += 1
                continue

            parts.append(Token(current, current_language))
            current = ""
            in_quotes = False
            quote_char = None
            index += 1
            continue

        # Space outside quotes starts new token.
        if char.isspace() and not in_quotes:
            if current:
                parts.append(Token(current, current_language))
                current = ""
            index += 1
            continue

        current += char
        index += 1

    if current:
        parts.append(Token(current, current_language))

    return parts


def test_split_by_spaces() -> None:
    """Test splitting by spaces."""

    assert parse_tokens("text1 text2 text3") == [
        Token("text1"),
        Token("text2"),
        Token("text3"),
    ]


def test_escaped_quotes() -> None:
    """Test escaped quotes."""

    assert parse_tokens(r'text1 "te\"xt2" text3') == [
        Token("text1"),
        Token('te"xt2'),
        Token("text3"),
    ]


def test_escaped_quotes2() -> None:
    """Test escaped quotes."""

    assert parse_tokens(r"text1 te\"xt2 text3") == [
        Token("text1"),
        Token('te"xt2'),
        Token("text3"),
    ]


def test_simple_command() -> None:
    """Test simple command."""

    assert parse_tokens("13:00 audiobook Idiot x1.25") == [
        Token("13:00"),
        Token("audiobook"),
        Token("Idiot"),
        Token("x1.25"),
    ]


def test_quotes() -> None:
    """Test quoted text."""

    assert parse_tokens('"text"') == [Token("text")]


def test_language_quotes() -> None:
    """Test language-specific quotes."""

    assert parse_tokens('en"text"') == [Token("text", "en")]
    assert parse_tokens('fr"text"') == [Token("text", "fr")]


def test_quotes_in_normal_text() -> None:
    """Test quoted text in normal text."""

    assert parse_tokens('text "text"') == [Token("text"), Token("text")]


def test_language_quotes_in_normal_text() -> None:
    """Test language-specific quotes in normal text."""

    assert parse_tokens('text en"text"') == [Token("text"), Token("text", "en")]

"""Tests for Vim syntax generation."""

from chronicle.event.sport import RunEvent
from chronicle.objects.core import Book, Mountain, Place, Project, Thing

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


# Object.get_vim_syntax — structure.


def test_object_vim_syntax_highlight_link() -> None:
    """`get_vim_syntax` emits a `highlight link` for the class."""
    assert "highlight link BookArguments" in Book.get_vim_syntax()


def test_object_vim_syntax_region() -> None:
    """`get_vim_syntax` emits a `syntax region` for the class."""
    assert "syntax region BookLine" in Book.get_vim_syntax()


def test_object_vim_syntax_region_start_prefix() -> None:
    """The region `start=` pattern uses the snake_case class prefix."""
    assert "start=/book" in Book.get_vim_syntax()


def test_object_vim_syntax_region_end() -> None:
    """The region ends at end of line."""
    assert "end=/$/" in Book.get_vim_syntax()


# Object.get_vim_syntax — patterns.


def test_object_vim_syntax_pattern_match_line() -> None:
    """`get_vim_syntax` emits a `syntax match` for pattern arguments."""
    # Mountain has a height pattern: (\d+(\.\d+)?)m
    syntax = Mountain.get_vim_syntax()
    assert "syntax match MountainArguments" in syntax


def test_object_vim_syntax_pattern_very_magic() -> None:
    r"""Pattern arguments use Vim's \v (very magic) flag."""
    syntax = Mountain.get_vim_syntax()
    assert r"/\v" in syntax


def test_object_vim_syntax_pattern_contained() -> None:
    """Pattern `syntax match` lines include `contained`."""
    syntax = Mountain.get_vim_syntax()
    assert "contained" in syntax


# Object.get_vim_syntax — named group stripping.


def test_object_vim_syntax_single_named_group_stripped() -> None:
    """A single named group `(?P<name>...)` is stripped from the pattern."""
    # Project uses ProgrammingLanguage whose pattern is `\.(?P<code>[a-z]+)`.
    syntax = Project.get_vim_syntax()
    assert "?P<" not in syntax


def test_object_vim_syntax_multiple_named_groups_all_stripped() -> None:
    r"""All named groups in a multi-group pattern are independently stripped.

    The OSM pattern has three named groups:
    `osm:(?P<type>[a-z]+)/(?P<id>\d+)/(?P<version>\d+)`

    After stripping it should become `osm:([a-z]+)/(\d+)/(\d+)`.
    The greedy `.*` in the current substitution matches from the first
    `?P<` to the *last* `>` in the string, collapsing all three groups
    into one and discarding the literal parts between them.
    Forward slashes between groups must also survive and be escaped as `\/`.
    """
    syntax = Place.get_vim_syntax()
    assert "?P<" not in syntax
    # The literal prefix, first capture group, and escaped slashes must survive.
    assert "osm:([a-z]+" in syntax
    assert r"\/" in syntax


# Object.get_vim_syntax — prefix arguments.


def test_object_vim_syntax_prefix_highlight_link() -> None:
    """`get_vim_syntax` emits `highlight link` for prefix arguments."""
    syntax = Thing.get_vim_syntax()
    assert "highlight link ThingPrefix Prefix" in syntax
    assert "highlight link ThingPrefixValue chronicleEventValue" in syntax


def test_object_vim_syntax_no_prefix_highlight_link_when_no_prefix_args() -> (
    None
):
    """`get_vim_syntax` does not emit prefix highlights if no prefix args."""
    assert "highlight link BookPrefix" not in Book.get_vim_syntax()


def test_object_vim_syntax_prefix_nextgroup() -> None:
    """`get_vim_syntax` emits `nextgroup` on prefix matches."""
    assert "nextgroup=ThingPrefixValue" in Thing.get_vim_syntax()


def test_object_vim_syntax_prefix_value_match() -> None:
    """`get_vim_syntax` emits a `PrefixValue` match for prefix arguments."""
    assert "syntax match ThingPrefixValue" in Thing.get_vim_syntax()


# Event.get_vim_syntax — structure.


def test_event_vim_syntax_strips_event_suffix() -> None:
    """`get_vim_syntax` removes the `Event` suffix from the class name."""
    syntax = RunEvent.get_vim_syntax()
    assert "syntax region RunLine" in syntax


def test_event_vim_syntax_highlight_link() -> None:
    """`get_vim_syntax` emits a `highlight link` for event arguments."""
    assert "highlight link RunArguments" in RunEvent.get_vim_syntax()


def test_event_vim_syntax_region_start_prefix() -> None:
    """The event region `start=` uses the snake_case prefix `run`."""
    assert "start=/run" in RunEvent.get_vim_syntax()


def test_event_vim_syntax_region_end() -> None:
    """The event region ends at end of line."""
    assert "end=/$/" in RunEvent.get_vim_syntax()


# Event.get_vim_syntax — known bugs.


def test_event_vim_syntax_pattern_very_magic() -> None:
    r"""Event pattern arguments should use Vim's \v (very magic) flag.

    `RunEvent` uses `Distance` whose patterns contain `(`, `)`, `+`
    and `?` — all of which require `\v` to work as regex operators in Vim.
    Without `\v` they are treated as literal characters.
    """
    assert r"/\v" in RunEvent.get_vim_syntax()


def test_event_vim_syntax_named_groups_stripped() -> None:
    """Named groups must be stripped from event patterns.

    `RunEvent` uses `Distance` whose patterns contain `(?P<v>...)`.
    Vim does not understand Python named-group syntax and raises E866/E871.
    """
    assert "?P<" not in RunEvent.get_vim_syntax()

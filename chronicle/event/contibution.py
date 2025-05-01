"""Contribution events.

Contribution events are events that represent a contribution to a crowd-sourced
projects as Wikipedia, OpenStreetMap, etc.
"""

from dataclasses import dataclass

from chronicle.event.core import Event
from chronicle.objects.core import Service


@dataclass
class ContributionEvent(Event):
    """Contribution event."""

    service: Service | None = None
    """Crowd-sourced project.

    E.g. English Wikipedia, German Wiktionary, OpenStreetMap, etc.
    """


@dataclass
class WikiContributionEvent(ContributionEvent):
    """Adding or editing a wiki page."""

    page_title: str | None = None
    """Title of the article or file name."""

    difference: int = 0
    """Difference in bytes between the old and new version of the page.

    Positive if the page was expanded, negative if it was contracted.
    """

    is_new: bool = False
    """Whether the page is new."""

    is_minor: bool = False
    """Whether the edit is a minor edit."""


class MapContributionEvent(ContributionEvent):
    """Adding or editing objects on a map."""

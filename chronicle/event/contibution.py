"""Contribution events.

Contribution events are events that represent a contribution to a crowd-sourced
projects as Wikipedia, OpenStreetMap, etc.
"""

from chronicle.event.core import Event


class ContributionEvent(Event):
    """Contribution event."""


class WikiContributionEvent(ContributionEvent):
    """Adding or editing a wiki page."""


class MapContributionEvent(ContributionEvent):
    """Adding or editing objects on a map."""

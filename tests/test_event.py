"""Tests for event parsing."""

from typing import Any

from chronicle.event.core import Objects
from chronicle.event.art import ListenPodcastEvent

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"

from event.value import Language

from objects import Podcast


def test_listen() -> None:
    """Test listen event parsing."""

    objects: Objects = Objects(
        {
            "inner_french": Podcast(
                title="Intermediate French Podcast",
                language=Language("fr"),
            )
        }
    )

    data: dict[str, Any] = {
        "time": "2022-01-01",
        "podcast_id": "inner_french",
        "episode": "15",
    }
    event: ListenPodcastEvent = ListenPodcastEvent(**data)
    assert event.podcast_id == "inner_french"
    assert event.episode == "15"

    assert (
        event.to_string(objects)
        == "listen podcast Intermediate French Podcast E 15"
    )

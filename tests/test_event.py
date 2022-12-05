"""Tests for event parsing."""

from typing import Any

from chronicle.event.core import Objects
from chronicle.event.listen import ListenPodcastEvent

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


def test_listen() -> None:
    """Test listen event parsing."""

    objects: Objects = Objects(
        podcasts={
            "inner_french": {
                "title": "Intermediate French Podcast",
                "language": "fr",
            }
        }
    )

    data: dict[str, Any] = {
        "time": "2022-01-01",
        "podcast_id": "inner_french",
        "kind": "podcast",
        "episode": 15,
    }
    event: ListenPodcastEvent = ListenPodcastEvent(**data)
    assert event.podcast_id == "inner_french"
    assert event.episode == "15"

    assert (
        event.to_string(objects)
        == "listen podcast Intermediate French Podcast E 15"
    )

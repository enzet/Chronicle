"""Harvest contribution data from Wikipedia."""

from dataclasses import dataclass
from datetime import datetime
from typing import override

import requests

from chronicle.event.contibution import WikiContributionEvent
from chronicle.harvest.core import Importer
from chronicle.time import Moment, Time
from chronicle.timeline import Timeline


@dataclass
class WikipediaImporter(Importer):
    """Importer for Wikipedia data."""

    username: str
    """Wikipedia username."""

    limit: int = 500
    """Maximum number of contributions to fetch."""

    @override
    def import_data(self, timeline: Timeline) -> None:
        """Import data from Wikipedia."""

        api_url: str = "https://en.wikipedia.org/w/api.php"

        parameters: dict = {
            "action": "query",
            "format": "json",
            "list": "usercontribs",
            "ucuser": self.username,
            "uclimit": self.limit,
            "ucprop": "timestamp|sizediff",
        }
        try:
            response: requests.Response = requests.get(
                api_url, params=parameters, timeout=10
            )
            response.raise_for_status()
            data: dict = response.json()

            for contrib in data["query"]["usercontribs"]:
                timestamp: datetime = datetime.strptime(
                    contrib["timestamp"], "%Y-%m-%dT%H:%M:%SZ"
                )
                difference: int = contrib["sizediff"]

                event: WikiContributionEvent = WikiContributionEvent(
                    Time.from_moment(Moment.from_datetime(timestamp)),
                    page_title=contrib["title"],
                    difference=difference,
                    is_new=contrib["new"],
                    is_minor=contrib["minor"],
                )
                timeline.events.append(event)

        except requests.RequestException as e:
            print(f"Error fetching Wikipedia contributions: {e}")

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

    @override
    def import_data(self, timeline: Timeline) -> None:
        """Import data from Wikipedia."""

        api_url: str = "https://en.wikipedia.org/w/api.php"
        parameters: dict = {
            "action": "query",
            "format": "json",
            "list": "usercontribs",
            "ucuser": self.username,
            "uclimit": 500,  # Maximum allowed per request
            "ucprop": "timestamp|sizediff|title|flags",
        }

        continue_token: str | None = None
        try:
            while True:
                # Add continue token if we have one.
                if continue_token:
                    parameters["uccontinue"] = continue_token

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
                        is_new="new" in contrib,
                        is_minor="minor" in contrib,
                    )
                    timeline.events.append(event)

                # Check if there are more pages.
                if "continue" in data and "uccontinue" in data["continue"]:
                    continue_token = data["continue"]["uccontinue"]
                else:
                    break  # No more pages to fetch.

        except requests.RequestException as error:
            print(f"Error fetching Wikipedia contributions: {error}.")

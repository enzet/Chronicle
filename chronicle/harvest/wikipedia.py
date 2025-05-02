"""Harvest contribution data from Wikipedia."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import override

import requests

from chronicle.event.contibution import WikiContributionEvent
from chronicle.harvest.core import Importer
from chronicle.time import Moment, Time
from chronicle.timeline import Timeline


@dataclass
class WikipediaImporter(Importer):
    """Importer for Wikipedia data."""

    url: str
    """Wikipedia URL."""

    username: str
    """Wikipedia username."""

    cache_path: Path
    """Path to cache directory."""

    def _get_cache_file(self) -> Path:
        """Get the cache file path."""
        return self.cache_path / f"{self.url}_{self.username}.json"

    def _load_cache(self) -> list[dict]:
        """Load cached contributions from file."""
        cache_file: Path = self._get_cache_file()
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as input_file:
                return json.load(input_file)
        return []

    def _save_cache(self, data: list[dict]) -> None:
        """Save contributions to cache file."""
        self.cache_path.mkdir(parents=True, exist_ok=True)
        with open(self._get_cache_file(), "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=2)

    def _create_event(self, contrib: dict) -> WikiContributionEvent:
        """Create a Wiki contribution event from contribution data."""
        timestamp: datetime = datetime.strptime(
            contrib["timestamp"], "%Y-%m-%dT%H:%M:%SZ"
        )
        return WikiContributionEvent(
            Time.from_moment(Moment.from_datetime(timestamp)),
            page_title=contrib["title"],
            difference=contrib["sizediff"],
            is_new="new" in contrib,
            is_minor="minor" in contrib,
        )

    @override
    def import_data(self, timeline: Timeline) -> None:
        """Import data from Wikipedia."""
        cache: list[dict] = self._load_cache()
        api_url: str = f"https://{self.url}/w/api.php"
        parameters: dict[str, str | int] = {
            "action": "query",
            "format": "json",
            "list": "usercontribs",
            "ucuser": self.username,
            "uclimit": 100,  # Maximum allowed per request is 500.
            "ucprop": "timestamp|sizediff|title|flags",
        }

        continue_token: str | None = None
        found_cached: bool = False
        event: WikiContributionEvent

        try:
            while True and not found_cached:
                if continue_token:
                    parameters["uccontinue"] = continue_token

                print(f"Requesting data for {self.url}...")
                response: requests.Response = requests.get(
                    api_url, params=parameters, timeout=10
                )
                response.raise_for_status()
                data: dict = response.json()

                contribs: list[dict] = data["query"]["usercontribs"]

                # Process current page.
                for contrib in contribs:
                    if contrib in cache:
                        found_cached = True
                    else:
                        event = self._create_event(contrib)
                        timeline.events.append(event)
                        cache.append(contrib)

                if (
                    "continue" in data
                    and "uccontinue" in data["continue"]
                    and not found_cached
                ):
                    continue_token = data["continue"]["uccontinue"]
                else:
                    break  # No more pages to fetch.

            # Save updated cache.
            self._save_cache(cache)

        except requests.RequestException as error:
            print(f"Error fetching Wikipedia contributions: {error}.")

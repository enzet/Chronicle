"""Harvest contribution data from Wikimedia."""

import argparse
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import override

import requests

from chronicle.event.contibution import WikiContributionEvent
from chronicle.harvest.core import Importer, ImportManager
from chronicle.time import Moment, Time
from chronicle.timeline import Timeline


class WikimediaImportManager(ImportManager):
    """Manager for Wikimedia import."""

    @staticmethod
    @override
    def add_argument(parser: argparse._ArgumentGroup) -> None:
        parser.add_argument(
            "--import-wikimedia",
            help=(
                "import contributions from Wikimedia projects, format: "
                "<username>@<url>, e.g. `User1@en.wikipedia.org`, "
                "`User2@wikidata.org`"
            ),
            metavar="<username>@<url>",
            nargs="+",
        )

    @staticmethod
    @override
    def process_arguments(
        arguments: argparse.Namespace, timeline: Timeline
    ) -> None:
        """Process arguments."""
        for value in arguments.import_wikimedia:
            username, url = value.split("@")
            logging.info("Importing Wikimedia contributions for `%s`.", url)
            WikimediaImporter(
                url=url,
                username=username,
                cache_path=Path(arguments.cache_path),
                cache_only=arguments.cache_only,
            ).import_data(timeline)


@dataclass
class WikimediaImporter(Importer):
    """Importer for Wikimedia data."""

    url: str
    """Wikimedia project URL."""

    username: str
    """Username in Wikimedia project."""

    cache_path: Path
    """Path to cache directory."""

    cache_only: bool
    """Use cache only."""

    def _get_cache_file(self) -> Path:
        """Get the cache file path."""
        return self.cache_path / f"{self.url}_{self.username}.json"

    def _load_cache(self) -> list[dict]:
        """Load cached contributions from file."""
        cache_file: Path = self._get_cache_file()
        if cache_file.exists():
            with open(cache_file, "r", encoding="utf-8") as input_file:
                data: list[dict] = json.load(input_file)
                return data
        return []

    def _save_cache(self, data: list[dict]) -> None:
        """Save contributions to cache file."""
        self.cache_path.mkdir(parents=True, exist_ok=True)
        with open(self._get_cache_file(), "w", encoding="utf-8") as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=2)

    def _create_event(self, contrib: dict) -> WikiContributionEvent:
        """Create a Wikimedia contribution event from contribution data."""
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
        """Import data from Wikimedia."""
        cache: list[dict] = self._load_cache()

        if self.cache_only:
            timeline.events.extend(
                self._create_event(contrib) for contrib in cache
            )
            return

        api_url: str = f"https://{self.url}/w/api.php"
        parameters: dict[str, str | int] = {
            "action": "query",
            "format": "json",
            "list": "usercontribs",
            "ucuser": self.username,
            "uclimit": 100,
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

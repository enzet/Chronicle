"""Wikidata-specific data."""

import json
import logging
from enum import Enum
from pathlib import Path
from textwrap import dedent
from typing import Any, Callable, Self

import urllib3

__author__ = "Sergey Vartanov"
__email__ = "me@enzet.ru"


class Item(Enum):
    """Wikidata item, main documentary unit of Wikidata."""

    FILM = 11424
    TELEVISION_SERIES = 5398426
    MOVING_IMAGE = 10301427

    def __repr__(self) -> str:
        return f"Q{self.value}"

    def __str__(self) -> str:
        return f"Q{self.value}"


class Property(Enum):
    """Wikidata property.

    Describes the data value of a statement and can be thought of as a category
    of data, for example, "color" for the data value "blue".
    """

    INSTANCE_OF = 31
    DIRECTOR = 57
    GENRE = 136
    SUBCLASS_OF = 279
    ORIGINAL_LANGUAGE_OF_FILM_OR_TV = 364
    ORIGINAL_BROADCASTER = 449
    COUNTRY_OF_ORIGIN = 495
    APPLIES_TO_PART = 518
    PUBLICATION_DATE = 577
    START_TIME = 580
    DISTRIBUTED_BY = 750
    TITLE = 1476

    def __repr__(self) -> str:
        return f"P{self.value}"

    def __str__(self) -> str:
        return f"P{self.value}"


class WikidataItem:
    """Wikidata item (elements starting with Q)."""

    def __init__(self, wikidata_id: int, data: dict) -> None:
        self.wikidata_id: int = wikidata_id
        self.data: dict = data["entities"][f"Q{wikidata_id}"]
        self.labels: dict = self.data["labels"]
        self.claims: dict = self.data["claims"]

    @classmethod
    def from_id(cls, wikidata_id: int, cache_path: Path) -> Self:
        """Create Wikidata item from ID.

        :param wikidata_id: ID of the Wikidata item with "Q" prefix
        :param cache_path: path to the cache file
        """
        return cls(
            wikidata_id,
            json.loads(
                get_data(
                    cache_path / f"{wikidata_id}.json",
                    get_wikidata_item,
                    str(wikidata_id),
                ).decode()
            ),
        )

    @staticmethod
    def get_float_value(claim: dict) -> float:
        """Parse float value from claim."""
        return float(claim["mainsnak"]["datavalue"]["value"]["amount"])

    def get_label(self, language: str = "en") -> str:
        """Get label of item."""

        value: str = self.labels[language]["value"]
        return value

    def get_claim(self, property_: Property, cache_path: Path) -> list[Any]:
        """Get claim of item by property."""

        if str(property_) not in self.claims:
            return []
        claims: list[dict] = self.claims[str(property_)]
        result: list[Any] = []
        for claim in claims:
            value: dict = claim["mainsnak"]["datavalue"]["value"]
            if "entity-type" in value and value["entity-type"] == "item":
                result.append(
                    WikidataItem.from_id(int(value["id"][1:]), cache_path)
                )
            else:
                result.append(value)

        return result

    def __eq__(self, other: object) -> bool:
        """Check whether two Wikidata items are equal."""

        if not isinstance(other, WikidataItem):
            return False
        return self.wikidata_id == other.wikidata_id

    def __hash__(self) -> int:
        return self.wikidata_id


def get_movie(title: str) -> str:
    """Get movie by title.

    Get a SPARQL query for every moving image (movie, animation, or TV series)
    with the specified title.
    """
    return dedent(
        f"""\
        SELECT ?item
        WHERE {{
            ?item wdt:{Property.INSTANCE_OF}/wdt:P279* wd:{Item.MOVING_IMAGE};
                  ?label "{title}"@en.
            SERVICE wikibase:label {{bd:serviceParam wikibase:language "en" .}}
        }}"""
    )


def request_sparql(query: str) -> bytes:
    """
    Request Wikidata with SPARQL query.  See
    https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service

    :param query: SPARQL query
    """
    data: bytes = (
        urllib3.PoolManager()
        .request(
            "GET",
            "https://query.wikidata.org/sparql",
            {"format": "json", "query": query},
        )
        .data
    )
    return data


def get_wikidata_item(wikidata_id: str) -> bytes:
    """Get Wikidata item structure.

    :param wikidata_id: ID of the Wikidata item with "Q" prefix
    """
    data: bytes = (
        urllib3.PoolManager()
        .request(
            "GET",
            "https://www.wikidata.org/wiki/Special:EntityData/"
            f"Q{wikidata_id}.json",
        )
        .data
    )
    return data


def get_data(cache_path: Path, function: Callable, argument: str) -> bytes:
    """
    Get some data from the cache if cache file exists, otherwise get it using
    function and store it to the cache.
    """
    if cache_path.exists():
        with cache_path.open("rb") as input_file:
            return input_file.read()
    logging.info("Request %s.", cache_path)
    data: bytes = function(argument)
    with cache_path.open("wb") as output_file:
        output_file.write(data)
    return data

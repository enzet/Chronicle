"""Utilities for requesting data from Wikidata."""

import logging
import sys
from typing import Any, Self

import requests

ITEM_CITY = 515
ITEM_MOVIE = 11424
ITEM_CITY_OR_TOWN = 7930989
ITEM_MEGACITY = 174844
ITEM_BIG_CITY = 1549591
ITEM_PORT_CITY = 2264924
ITEM_URBAN_TYPE_SETTLEMENT = 2989457
ITEM_ANCIENT_CITY = 15661340

ITEM_CITIES: list[int] = [
    ITEM_CITY,
    ITEM_CITY_OR_TOWN,
    ITEM_MEGACITY,
    ITEM_BIG_CITY,
    ITEM_PORT_CITY,
    ITEM_URBAN_TYPE_SETTLEMENT,
    ITEM_ANCIENT_CITY,
]

PROPERTY_COUNTRY = 17
PROPERTY_INSTANCE_OF = 31
PROPERTY_COORDINATE_LOCATION = 625

WIKIDATA_API_URL: str = "https://www.wikidata.org/w/api.php"

REQUEST_HEADERS: dict[str, str] = {
    "User-Agent": "Chronicle/0.1 (+https://github.com/enzet/Chronicle)",
}

logger: logging.Logger = logging.getLogger(__name__)


class WikidataItem:
    """Wikidata item."""

    def __init__(self, data: dict) -> None:
        self.data: dict = data
        self.id: int = int(data["id"][1:])
        self.labels: dict = data["labels"]
        self.claims: dict = data["claims"]

    def get_label(self, language: str = "en") -> str:
        """Get label of item."""
        return self.labels[language]["value"]

    def get_coordinates(self) -> tuple[float, float] | None:
        """Get coordinates of item."""
        coordinates: dict[str, Any] | None = self.data.get("claims", {}).get(
            f"P{PROPERTY_COORDINATE_LOCATION}"
        )
        if not coordinates:
            return None
        latitude: float = float(
            coordinates[0]["mainsnak"]["datavalue"]["value"]["latitude"]
        )
        longitude: float = float(
            coordinates[0]["mainsnak"]["datavalue"]["value"]["longitude"]
        )
        return latitude, longitude

    def get_country(self) -> Self:
        """Get country of item."""
        country: dict[str, Any] | None = self.data.get("claims", {}).get(
            f"P{PROPERTY_COUNTRY}"
        )
        if not country:
            message = f"No country found for item {self.id}."
            raise ValueError(message)
        return WikidataItem(country)


class Wikidata:
    """Harvest data from Wikidata."""

    def request_item(self, item_name: str, types: list[int]) -> dict:
        """Request item data from Wikidata.

        :param item_name: name of the item
        :param types: list of types to search for
        :return: Wikidata item data
        """
        search_parameters: dict[str, str] = {
            "action": "wbsearchentities",
            "format": "json",
            "language": "en",
            "search": item_name,
            "type": "item",
            "limit": "20",
        }

        try:
            response: requests.Response = requests.get(
                WIKIDATA_API_URL,
                params=search_parameters,
                headers=REQUEST_HEADERS,
                timeout=10,
            )
            response.raise_for_status()
        except requests.RequestException as error:
            message: str = (
                f"Failed to search Wikidata for `{item_name}`: {error}."
            )
            raise RuntimeError(message) from error

        results: list[dict[str, Any]] = response.json().get("search", [])
        ids: list[str] = [
            item["id"] for item in results if item.get("id", "").startswith("Q")
        ]

        if not ids:
            message = f"No Wikidata search results found for `{item_name}`."
            raise ValueError(message)

        for chunk_start in range(0, len(ids), 50):
            chunk_ids: list[str] = ids[chunk_start : chunk_start + 50]
            entity_parameters: dict[str, str] = {
                "action": "wbgetentities",
                "format": "json",
                "ids": "|".join(chunk_ids),
                "props": "claims|labels",
            }

            try:
                entity_response: requests.Response = requests.get(
                    WIKIDATA_API_URL,
                    params=entity_parameters,
                    headers=REQUEST_HEADERS,
                    timeout=10,
                )
                entity_response.raise_for_status()
            except requests.RequestException as error:
                logger.warning(
                    "Failed to fetch Wikidata entity details for `%s`: %s.",
                    chunk_ids,
                    error,
                )
                continue

            entities: dict[str, Any] = entity_response.json().get(
                "entities", {}
            )
            print(f"Found {len(entities)} entities.")

            for entity_id, entity_data in entities.items():
                claims: dict[str, Any] = entity_data.get("claims", {})
                instance_ofs: list[dict[str, Any]] = claims.get(
                    f"P{PROPERTY_INSTANCE_OF}", []
                )

                for type_ in types:
                    if _claims_include_type(instance_ofs, type_):
                        return WikidataItem(entities[entity_id])

        message = (
            f"No Wikidata item `{item_name}` with instance Q{type_} found."
        )
        raise ValueError(message)

    def request_city(self, city_name: str) -> WikidataItem:
        """Request city data from Wikidata."""
        return self.request_item(city_name, ITEM_CITIES)

    def request_movie(self, movie_name: str) -> WikidataItem:
        """Request movie data from Wikidata."""
        return self.request_item(movie_name, [ITEM_MOVIE])


def _claims_include_type(claims: list[dict[str, Any]], type_id: int) -> bool:
    """Check whether claims list contains instance of type."""
    for claim in claims:
        mainsnak: dict[str, Any] | None = claim.get("mainsnak")
        if not mainsnak:
            continue
        datavalue: dict[str, Any] | None = mainsnak.get("datavalue")
        if not datavalue:
            continue
        value: dict[str, Any] | None = datavalue.get("value")
        if not value:
            continue
        numeric_id: int | None = value.get("numeric-id")
        if numeric_id == type_id:
            return True
    return False


if __name__ == "__main__":
    wikidata: Wikidata = Wikidata()

    type_, name = sys.argv[1], sys.argv[2]

    if type_ == "city":
        item: WikidataItem = wikidata.request_city(name)
        coordinates = item.get_coordinates()
        label = item.get_label("en")
        message_parts: list[str] = [f"city @{name} ="]
        if label:
            message_parts.append(label)
        if coordinates:
            message_parts.append(f"lat: {coordinates[0]} lon: {coordinates[1]}")
        message_parts.append(f"Q{item.id}")
        print(" ".join(message_parts))
    elif type_ == "movie":
        print(wikidata.request_movie(name))
    else:
        print(f"Unknown type: {type_}")

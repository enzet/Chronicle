"""Harvest data from external services."""

import argparse
from abc import ABC, abstractmethod

from chronicle.timeline import Timeline


class ImportManager(ABC):
    """Manager for import of data from an external service."""

    @staticmethod
    @abstractmethod
    def add_argument(parser: argparse._ArgumentGroup) -> None:
        """Add arguments to the parser."""
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def process_arguments(
        arguments: argparse.Namespace, timeline: Timeline
    ) -> None:
        """Process arguments."""
        raise NotImplementedError


class Importer(ABC):
    """Importer for data from an external service."""

    @abstractmethod
    def import_data(self, timeline: Timeline) -> None:
        """Import data from an external service.

        :param timeline: timeline to store new events
        """
        raise NotImplementedError

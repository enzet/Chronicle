"""Harvest data from external services."""

from abc import ABC, abstractmethod

from chronicle.timeline import Timeline


class Importer(ABC):
    """Importer for data from an external service."""

    @abstractmethod
    def import_data(self, timeline: Timeline) -> None:
        """Import data from an external service.

        :param timeline: timeline to store new events
        """
        raise NotImplementedError()

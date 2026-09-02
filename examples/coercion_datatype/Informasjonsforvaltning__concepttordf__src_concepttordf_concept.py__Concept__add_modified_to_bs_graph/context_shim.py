# Context shim (see meta.json): src/concepttordf/betydningsbeskrivelse.py
# from Informasjonsforvaltning/concepttordf@b06016d2fff0ab2a2e389b0b39fcd47225a65b0d,
# copied verbatim. original.py's `from .betydningsbeskrivelse import
# Betydningsbeskrivelse, RelationToSource` is a relative import that raises
# `ImportError: attempted relative import with no known parent package`
# outside the concepttordf package; the region itself never instantiates or
# inspects either name (Betydningsbeskrivelse is an abstract base class used
# only as a parameter annotation, RelationToSource is imported at module
# level but not referenced in the extracted lines at all), so a verbatim
# copy -- rather than a reduced stand-in -- is both simplest and exact.
#
# Identical bindings for both representations.
"""Concept module for mapping abstract class Betydningsbeskrivelse to rdf."""

from abc import ABC, abstractmethod
from datetime import date
from enum import Enum


class RelationToSource(Enum):
    """An enum representing relations to source."""

    sitatFraKilde = "quoteFromSource"
    basertPaKilde = "basedOnSource"
    egendefinert = "noSource"


class Betydningsbeskrivelse(ABC):
    """A class representing a concept.

    Attributes:
        text:
        remark:
        scope:
        relationtosource:
        source:
        modified:
        example:
    """

    @abstractmethod
    def __init__(self) -> None:
        """Inits an object with default values."""

    @property
    def text(self) -> dict:
        """Text attribute.

        Returns:
            a dict with key as language code (str) and value text (str)
        """
        return self._text

    @text.setter
    def text(self, text: dict) -> None:
        self._text = text

    @property
    def remark(self) -> dict:
        """Remark attribute.

        Returns:
            a dict with key as language code (str) and value remark (str)
        """
        return self._remark

    @remark.setter
    def remark(self, remark: dict) -> None:
        self._remark = remark

    @property
    def scope(self) -> dict:
        """Scope attribute.

        Returns:
            a dict with key as language code (str) and value scope (str)
        """
        return self._scope

    @scope.setter
    def scope(self, scope: dict) -> None:
        self._scope = scope

    @property
    def relationtosource(self) -> str:
        """Relationtosource attribute.

        Returns:
            a relationtype to source (str)
        """
        return self._relationtosource

    @relationtosource.setter
    def relationtosource(self, relationtosource: str) -> None:
        self._relationtosource = relationtosource

    @property
    def source(self) -> dict:
        """Source attribute.

        Returns:
            a dict with key as language code (str) and value remark (str)
        """
        return self._source

    @source.setter
    def source(self, source: dict) -> None:
        self._source = source

    @property
    def modified(self) -> date:
        """Source attribute.

        Returns:
            the date on which the item was last updated
        """
        return self._modified

    @modified.setter
    def modified(self, modified: date) -> None:
        self._modified = modified

    @property
    def example(self) -> dict:
        """Example attribute.

        Returns:
            a dict with key as language code (str) and value example (str)
        """
        return self._example

    @example.setter
    def example(self, example: dict) -> None:
        self._example = example

    @abstractmethod
    def to_rdf(self) -> str:
        """Convert the object to RDF format.

        Returns:
            RDF representation as a string
        """

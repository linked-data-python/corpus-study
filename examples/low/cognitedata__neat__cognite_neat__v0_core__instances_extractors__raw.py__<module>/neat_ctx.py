"""Context shim for the RAWExtractor module region.

The region is a whole module of cognitedata/neat@4042d3e96d
(``cognite/neat/_v0/core/_instances/extractors/_raw.py``).  It imports from
the Cognite Python SDK and from four neat-internal modules, none of which is
installed in the eval venv; two of those imports are package-relative and
could not resolve in an isolated file anyway.  This shim supplies exactly the
names the module imports:

* ``Triple`` — copied from ``cognite/neat/_v0/core/_shared.py`` line 76.
* ``DEFAULT_RAW_URI`` — copied from ``cognite/neat/_v0/core/_constants.py``
  line 111.
* ``DEFAULT_EMPTY_VALUES`` / ``DictExtractor`` — copied from
  ``…/extractors/_dict.py`` lines 15-83 (only ``DictExtractor``, not its
  ``DMSPropertyExtractor`` subclass, which needs the SDK's data-modeling
  types); ``string_to_ideal_type`` copied from
  ``cognite/neat/_v0/core/_utils/auxiliary.py`` lines 123-144.
* ``BaseExtractor`` — reduced from ``…/extractors/_base.py`` to the abstract
  ``extract`` the region overrides (the rest pulls in neat's data-model and
  provenance packages).
* ``Row`` / ``RowList`` / ``SequenceNotStr`` / ``NeatClient`` — stand-ins for
  the Cognite SDK types.  ``Row`` is what the region reads (``row.key`` and
  ``row.columns``), ``RowList`` the list wrapper it also has to handle, and
  ``NeatClient`` replays a canned ``client.raw.rows(...)`` result instead of
  calling the CDF REST API.

``original.py`` and ``translated.ldpy`` import this shim identically; only
the region itself differs between them.
"""

import json
import urllib.parse
from collections.abc import Iterable, Mapping, Sequence, Set
from datetime import datetime
from typing import Any, TypeAlias

from rdflib import XSD, Literal, Namespace, URIRef

# --- cognite/neat/_v0/core/_shared.py --------------------------------------
Triple: TypeAlias = tuple[URIRef, URIRef, Literal | URIRef]

# --- cognite/neat/_v0/core/_constants.py -----------------------------------
DEFAULT_RAW_URI = "http://purl.org/cognite/raw#"

# --- cognite/neat/_v0/core/_utils/auxiliary.py -----------------------------


def string_to_ideal_type(input_string: str) -> int | bool | float | datetime | str:
    try:
        # Try converting to int
        return int(input_string)
    except ValueError:
        try:
            # Try converting to float
            return float(input_string)  # type: ignore
        except ValueError:
            if input_string.lower() == "true":
                # Return True if input is 'true'
                return True
            elif input_string.lower() == "false":
                # Return False if input is 'false'
                return False
            else:
                try:
                    # Try converting to datetime
                    return datetime.fromisoformat(input_string)  # type: ignore
                except ValueError:
                    # Return the input string if no conversion is possible
                    return input_string


# --- cognite/neat/_v0/core/_instances/extractors/_base.py (reduced) --------


class BaseExtractor:
    """This is the base class for all extractors. It defines the interface that
    extractors must implement.
    """

    def extract(self) -> Iterable[Triple]:
        raise NotImplementedError()


# --- cognite/neat/_v0/core/_instances/extractors/_dict.py ------------------

DEFAULT_EMPTY_VALUES = frozenset(
    {"nan", "null", "none", "", " ", "nil", "n/a", "na", "unknown", "undefined"})


class DictExtractor(BaseExtractor):
    def __init__(
        self,
        id_: URIRef,
        data: Mapping[str, Any],
        namespace: Namespace,
        uri_ref_keys: set[str] | None = None,
        empty_values: Set[str] = DEFAULT_EMPTY_VALUES,
        str_to_ideal_type: bool = False,
        unpack_json: bool = False,
    ) -> None:
        self.id_ = id_
        self.namespace = namespace
        self.data = data
        self.uri_ref_keys = uri_ref_keys or set()
        self.empty_values = empty_values
        self.str_to_ideal_type = str_to_ideal_type
        self.unpack_json = unpack_json

    def extract(self) -> Iterable[Triple]:
        for key, value in self.data.items():
            for predicate_str, object_ in self._get_predicate_objects_pair(
                    key, value, self.unpack_json):
                yield self.id_, self.namespace[urllib.parse.quote(predicate_str)], object_

    def _get_predicate_objects_pair(
        self, key: str, value: Any, unpack_json: bool
    ) -> Iterable[tuple[str, Literal | URIRef]]:
        if key in self.uri_ref_keys and not isinstance(value, dict | list):
            # exist if key is meant to form a URIRef
            yield key, URIRef(self.namespace[urllib.parse.quote(value)])
        elif isinstance(value, float | bool | int):
            yield key, Literal(value)
        elif isinstance(value, str):
            yield key, Literal(string_to_ideal_type(value)) if self.str_to_ideal_type else Literal(value)
        elif isinstance(value, dict) and unpack_json:
            yield from self._unpack_json(value)
        elif isinstance(value, dict):
            # This object is a json object.
            yield key, Literal(json.dumps(value), datatype=XSD._NS["json"])
        elif isinstance(value, list):
            for item in value:
                yield from self._get_predicate_objects_pair(key, item, False)

    def _unpack_json(self, value: dict, parent: str | None = None) -> Iterable[tuple[str, Literal | URIRef]]:
        for sub_key, sub_value in value.items():
            key = f"{parent}_{sub_key}" if parent else sub_key
            if isinstance(sub_value, str):
                if sub_value.casefold() in self.empty_values:
                    continue
                if self.str_to_ideal_type:
                    yield key, Literal(string_to_ideal_type(sub_value))
                else:
                    yield key, Literal(sub_value)
            elif isinstance(sub_value, int | float | bool):
                yield key, Literal(sub_value)
            elif isinstance(sub_value, dict):
                yield from self._unpack_json(sub_value, key)
            elif isinstance(sub_value, list):
                for no, item in enumerate(sub_value, 1):
                    if isinstance(item, dict):
                        yield from self._unpack_json(item, f"{key}_{no}")
                    else:
                        yield from self._get_predicate_objects_pair(key, item, self.unpack_json)
            else:
                yield key, Literal(str(sub_value))


# --- stand-ins for the Cognite SDK ----------------------------------------

SequenceNotStr = Sequence


class Row:
    """Stand-in for cognite.client.data_classes.Row (key + columns)."""

    def __init__(self, key: str, columns: dict):
        self.key = key
        self.columns = columns


class RowList(list):
    """Stand-in for cognite.client.data_classes.RowList."""


class _Raw:
    def __init__(self, tables):
        self._tables = tables

    def rows(self, db_name, table_name, partitions=None, chunk_size=None):
        return self._tables[table_name]


class NeatClient:
    """Stand-in for neat's CDF client: replays a canned RAW table."""

    def __init__(self, tables):
        self.raw = _Raw(tables)

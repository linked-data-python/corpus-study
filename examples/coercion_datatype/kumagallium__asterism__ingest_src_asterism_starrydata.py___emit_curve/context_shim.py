# Context shim (see meta.json), for kumagallium/asterism@f0977d4d3a,
# ingest/src/asterism/starrydata.py. The `asterism` package is not installed,
# and the region calls six names it does not define:
#
#   * parse_float_array, strip_quoted     -- asterism/text.py, copied verbatim;
#   * parse_project_names, parse_curator_timestamp (and _TZ_NAME_SUFFIX they
#     use) -- asterism/starrydata.py, same file as the region, copied verbatim;
#   * quantity_kind_iri, unit_iri         -- asterism/qudt.py, copied verbatim
#     with the engine around them; only `_load_map` differs: the real one finds
#     the table through asterism.datasets.datasets_root(), here the same file
#     (datasets/starrydata/qudt_map.yaml, copied verbatim as qudt_map.yaml next
#     to this shim) is read from the shim's directory.
#
# Identical bindings for both representations.
from __future__ import annotations

import functools
import json
import logging
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

import yaml

logger = logging.getLogger("asterism.qudt")

QUANTITY_KIND_BASE: Final[str] = "http://qudt.org/vocab/quantitykind/"
UNIT_BASE: Final[str] = "http://qudt.org/vocab/unit/"
_EMPTY_MAP: Final[dict[str, dict[str, str]]] = {"quantity_kinds": {}, "units": {}}


@functools.lru_cache(maxsize=1)
def _load_map() -> dict[str, dict[str, str]]:
    path = Path(__file__).resolve().parent / "qudt_map.yaml"
    if not path.is_file():
        logger.warning("qudt_map.yaml not found; QUDT normalization disabled")
        return _EMPTY_MAP
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    quantity_kinds = data.get("quantity_kinds") or {}
    units = data.get("units") or {}
    # Normalize quantity-kind keys to lowercase once at load time so lookups
    # are O(1) and case-insensitive without re-lowercasing the whole table.
    quantity_kinds = {str(k).strip().lower(): str(v) for k, v in quantity_kinds.items()}
    units = {str(k).strip(): str(v) for k, v in units.items()}
    return {"quantity_kinds": quantity_kinds, "units": units}


def quantity_kind_iri(property_name: str | None) -> str | None:
    """Return the QUDT QuantityKind IRI for a starrydata property name, or None."""
    if not property_name:
        return None
    local = _load_map()["quantity_kinds"].get(property_name.strip().lower())
    return QUANTITY_KIND_BASE + local if local else None


def unit_iri(unit_string: str | None) -> str | None:
    """Return the QUDT Unit IRI for a starrydata unit string, or None.

    Matching is case-sensitive: unit symbols differ by case (e.g. ``S`` siemens
    vs ``s`` second, ``T`` tesla vs ``t`` tonne).
    """
    if not unit_string:
        return None
    local = _load_map()["units"].get(unit_string.strip())
    return UNIT_BASE + local if local else None


def parse_float_array(raw: str) -> list[float]:
    """JSON 数値配列を ``list[float]`` にパース。

    失敗した個別要素は除外し (NaN / None / 非数値文字列など)、配列自体が壊れていれば
    空リストを返す。
    """
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    out: list[float] = []
    for v in data:
        try:
            if v is None:
                continue
            fv = float(v)
            if fv != fv:  # NaN check
                continue
            out.append(fv)
        except (TypeError, ValueError):
            continue
    return out


def strip_quoted(value: str) -> str:
    """JSON-quoted 文字列なら剥がす。それ以外はトリムして返す。"""
    v = value.strip()
    if len(v) >= 2 and v[0] == v[-1] == '"':
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v.strip('"')
    return v


_TZ_NAME_SUFFIX = re.compile(r"\s*\([^)]*\)\s*$")  # " (Japan Standard Time)"


def parse_curator_timestamp(raw: str) -> str | None:
    """Parse a JS Date.toString() timestamp to a UTC ISO 8601 instant.

    Returns e.g. ``"2017-09-01T09:19:39Z"`` for a ``GMT+0900`` input. Returns
    ``None`` if the string can't be parsed OR carries no timezone — in the
    latter case the instant is genuinely unknown, so we emit no prov:atTime
    rather than fabricate one (the raw local string still lives on
    dcterms:created).
    """
    if not raw:
        return None
    s = _TZ_NAME_SUFFIX.sub("", raw.strip())  # drop trailing "(...)" tz name
    s = s.replace("GMT", "").strip()          # "GMT+0900" -> "+0900" for %z
    try:
        dt = datetime.strptime(s, "%a %b %d %Y %H:%M:%S %z")
    except ValueError:
        return None
    # Normalize to a UTC instant. isoformat() yields the "+00:00" offset form;
    # rdflib canonicalizes xsd:dateTime to that same form anyway (it rewrites a
    # trailing "Z" to "+00:00"), so we emit "+00:00" directly for consistency
    # between this helper and what actually lands in the graph / Oxigraph.
    return dt.astimezone(UTC).isoformat()


def parse_project_names(raw: str) -> list[str]:
    if not raw:
        return []
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [str(x).strip() for x in data if str(x).strip()]

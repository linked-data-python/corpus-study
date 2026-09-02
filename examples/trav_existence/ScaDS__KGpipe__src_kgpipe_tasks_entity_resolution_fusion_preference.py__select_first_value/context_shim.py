# Context shim (see meta.json): minimal stand-ins for the framework types
# `select_first_value` depends on, reproduced from ScaDS/KGpipe@67ca171cfd
# and from the region's OWN file (preference.py:1-25, above the extracted
# window) at that commit. Identical bindings for both representations.
#
# `kgpipe`/`kgpipe_tasks` (this project) and `kgcore` (an external
# dependency of it) are NOT on PyPI (`pip index versions kgpipe`/`kgcore`
# both report "No matching distribution found"), so the region cannot run
# against the real packages; nothing here invents behaviour the real
# classes do not have, it only drops framework plumbing this region's RDF
# operations do not depend on.
import json
from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path


class DataFormat(str, Enum):
    """Reproduced from kgpipe/common/model/data.py's `BasicDataFormats`
    (aliased to `DataFormat` in kgpipe/common/models.py) -- only the one
    member this region's decorator metadata names."""
    RDF_NTRIPLES = "nt"


@dataclass
class Data:
    """Reproduced from kgpipe/common/model/data.py's `Data(BaseModel)`:
    only the `path` field this region reads (`inputs["source"].path`,
    `outputs["output"].path`, ...); the real class also carries a
    `format` field and constructor overloads irrelevant here."""
    path: Path


@dataclass
class TrackRecord:
    """Reproduced from preference.py:20-25 (`class TrackRecord(BaseModel)`,
    in the SAME file as the region, just above the extracted window) as a
    plain dataclass rather than a pydantic model, to avoid adding pydantic
    as a dependency for a type the translated ISLAND code never touches.
    `__post_init__` reproduces pydantic's field coercion to `str` -- the
    region passes `URIRef`/`Literal` values (both `str` subclasses in
    rdflib) into fields pydantic declares as plain `str`, and `model_dump`
    must return genuinely JSON-serialisable values either way."""
    original_subject: str
    subject: str
    original_predicate: str
    predicate: str
    original_object: str
    object: str

    def __post_init__(self):
        for f in ("original_subject", "subject", "original_predicate",
                  "predicate", "original_object", "object"):
            setattr(self, f, str(getattr(self, f)))

    def model_dump(self):
        return asdict(self)


class Registry:
    """Stand-in for kgpipe/common/registry.py's `Registry`. The real
    `.task(...)` classmethod (registry.py:67-82) wraps the decorated
    function into a `KgTask` object and registers it in a global registry
    -- machinery for the pipeline runner, unrelated to this region's RDF
    operations. Reproduced as the identity decorator so
    `select_first_value` stays directly callable by this study's driver,
    exactly as it is inside the real package (`KgTask.__call__` forwards
    to the wrapped function)."""

    @staticmethod
    def task(**kwargs):
        def decorator(fn):
            return fn
        return decorator


class _Property:
    def __init__(self, uri, max_cardinality):
        self.uri = uri
        self.max_cardinality = max_cardinality


class _Ontology:
    def __init__(self, properties):
        self.properties = properties


class OntologyUtil:
    """Stand-in for kgcore.api.ontology.OntologyUtil (external package, not
    on PyPI -- see module docstring). `load_ontology_from_file` here reads
    a small JSON list of `{"uri": ..., "max_cardinality": ...}` objects
    written by the driver, rather than parsing a real ontology file, but
    hands the region the same `ontology.properties[i].uri` /
    `.max_cardinality` shape it reads (preference.py:33-34)."""

    @staticmethod
    def load_ontology_from_file(path):
        with open(path) as f:
            entries = json.load(f)
        return _Ontology([_Property(e["uri"], e["max_cardinality"])
                          for e in entries])


TARGET_ONTOLOGY_NAMESPACE = "http://kg.org/ontology/"
# ^ reproduced verbatim from kgpipe/common/config.py:18.

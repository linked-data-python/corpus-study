# Context shim (see meta.json): swh.indexer.namespaces and produce_terms
# transcribed VERBATIM from SoftwareHeritage/swh-indexer@95f3e654628b68ea963d06fb83b93011a6c2b47e
# (swh/indexer/namespaces.py, swh/indexer/metadata_mapping/base.py -- see
# corpus/repos/SoftwareHeritage__swh-indexer/ for the local clone), so the
# region executes outside the package: `swh` is not installed in the study
# venv (ModuleNotFoundError), and the original module also imports a sibling
# package (`.base`) that does not exist standalone. BaseExtrinsicMapping and
# JsonMapping are name-only stand-ins -- translate_parent never instantiates
# or calls into them, it only receives them as an (unused) import. Identical
# bindings for both representations.
from typing import Any, Callable, TypeVar

import rdflib
from rdflib import Namespace as _Namespace

SCHEMA = _Namespace("http://schema.org/")
CODEMETA = _Namespace("https://codemeta.github.io/terms/")
FORGEFED = _Namespace("https://forgefed.org/ns#")
ACTIVITYSTREAMS = _Namespace("https://www.w3.org/ns/activitystreams#")
XSD = _Namespace("http://www.w3.org/2001/XMLSchema#")

TTranslateCallable = TypeVar(
    "TTranslateCallable",
    bound=Callable[[Any, rdflib.Graph, rdflib.term.BNode, Any], None],
)


def produce_terms(*uris: str) -> Callable[[TTranslateCallable], TTranslateCallable]:
    """Returns a decorator that marks the decorated function as adding
    the given terms to the ``translated_metadata`` dict"""

    def decorator(f: TTranslateCallable) -> TTranslateCallable:
        if not hasattr(f, "produced_terms"):
            f.produced_terms = []  # type: ignore
        f.produced_terms.extend(uris)  # type: ignore
        return f

    return decorator


class BaseExtrinsicMapping:
    """Name-only stand-in: unused by translate_parent's own body."""


class JsonMapping(BaseExtrinsicMapping):
    """Name-only stand-in: unused by translate_parent's own body."""

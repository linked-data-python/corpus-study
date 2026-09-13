# Context shim (see meta.json), for TheWorldAvatar/mcp-tool-layer@c440a33e08 :
# src/ontospecies_extension/operations/ontospecies_extension.py.
#
# OS, _class, _mint_hash_iri, _ensure_type_with_label, _is_abs_iri,
# _list_species_summaries and locked_graph are module-level helpers that
# add_elemental_analysis_data_to_species (lines 356-411 of the source file)
# calls but that are defined elsewhere in the same file -- same family as
# the sibling region add_isolated/..._add_atomic_weight_to_element, whose
# context_shim.py this one mirrors.
#
# _mint_hash_iri is made deterministic and call-scoped: the real
# implementation hashes datetime.now(timezone.utc), which would mint a
# different IRI on every call -- including the two separate calls (original
# vs translated) this pilot makes -- breaking the isomorphism check for a
# reason that has nothing to do with the translation. Here it numbers mints
# within a single call to the region: the counter resets when locked_graph()
# is entered, which the region does exactly once per call, as its very first
# statement, so `_mint_hash_iri("WeightPercentage")` called twice in ONE
# call (calculated + experimental branches) still mints two DISTINCT nodes,
# and the two sides mint the very same sequence for the very same call.
#
# locked_graph is simplified to `yield Graph()` (no FileLock/TTL
# persistence -- an external dependency the region body never inspects),
# but pre-populated from `SEED` (set by driver.py from fixture.ttl before
# each call): unlike the add_isolated sibling, this region READS the graph
# (the "species exists" check) before it writes to it, so the graph must
# arrive non-empty. The graph is made observable the same way as the
# sibling too: via LAST_GRAPH, snapshotted by driver.py right after each
# call, since it is neither a parameter nor part of the return value.
#
# _list_species_summaries is a stand-in for a catalog-formatting helper: the
# region only uses its return value as an opaque string interpolated into an
# error message, so a fixed empty string is faithful (same string on both
# sides, for the same reason a hollow catalog would be).
from contextlib import contextmanager
from typing import Optional
from urllib.parse import urlparse

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

OS = Namespace("http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#")
INST_BASE = "https://www.theworldavatar.com/kg/OntoSpecies/instance"


def _class(ns: Namespace, local: str) -> URIRef:
    return getattr(ns, local)


def _is_abs_iri(s: str) -> bool:
    try:
        u = urlparse(s)
        return bool(u.scheme) and bool(u.netloc)
    except Exception:
        return False


def _ensure_type_with_label(g: Graph, iri: URIRef, cls: URIRef, label: Optional[str] = None) -> None:
    g.add((iri, RDF.type, cls))
    if label is not None:
        g.set((iri, RDFS.label, Literal(label)))


def _list_species_summaries(g: Graph, limit: int) -> str:
    return ""


# Reset by locked_graph() on every call (the region's own first statement);
# read by _mint_hash_iri. See module docstring above.
_MINT_COUNTER = [0]


def _mint_hash_iri(class_local: str) -> URIRef:
    _MINT_COUNTER[0] += 1
    return URIRef(f"{INST_BASE}/{class_local}/deterministic-test-hash-{_MINT_COUNTER[0]}")


# Set by driver.py before each call: the triples the fresh graph should
# already contain, so the region's own "species exists" check has something
# to find. See module docstring above.
SEED: list = []

# Set by locked_graph() right before yielding, and read by driver.py right
# after each call -- see driver.py for the non-overlapping sequencing this
# relies on (same convention as the add_isolated sibling above).
LAST_GRAPH = None


@contextmanager
def locked_graph(timeout: float = 30.0):
    global LAST_GRAPH
    _MINT_COUNTER[0] = 0
    g = Graph()
    for t in SEED:
        g.add(t)
    LAST_GRAPH = g
    yield g

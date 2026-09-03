# Context shim (see meta.json), for TheWorldAvatar/mcp-tool-layer@c440a33e08 :
# src/ontospecies_extension/operations/ontospecies_extension.py.
#
# _is_abs_iri (lines 49-53 of the source file) is a module-level helper
# delete_triple (lines 603-622) calls but that is defined elsewhere in the
# same file. Copied verbatim:
#
#     def _is_abs_iri(s: str) -> bool:
#         try:
#             u = urlparse(s); return bool(u.scheme) and bool(u.netloc)
#         except Exception:
#             return False
#
# locked_graph (lines 181-201) is simplified. The real implementation
# acquires a FileLock and parses/serialises a TTL file under
# data/<hash>/memory_ontospecies/ -- filesystem locking and persistence that
# delete_triple's own body never inspects (it only reads/writes the yielded
# `g` inside the `with` block) and that would need the `filelock` package
# plus a writable data directory: an external dependency out of reach here
# and out of scope for this region (same precedent as the sibling region
# add_atomic_weight_to_element/context_shim.py, stratum add_isolated).
#
# Unlike that sibling, delete_triple does not only ADD to a graph that starts
# empty: it checks for and removes an EXISTING triple, so a `locked_graph`
# that always yields a fresh empty graph would make every case a "no such
# triple" case. Persistence is replaced here by a module-level SEED_GRAPH the
# driver populates right before each call (what delete_triple should find
# already in `g`), and LAST_GRAPH, overwritten with the post-call graph when
# the `with` block exits -- so the driver can inspect what remains after the
# removal attempt. See driver.py for how the two are sequenced.
from contextlib import contextmanager
from urllib.parse import urlparse

from rdflib import Graph


def _is_abs_iri(s: str) -> bool:
    try:
        u = urlparse(s)
        return bool(u.scheme) and bool(u.netloc)
    except Exception:
        return False


SEED_GRAPH = None
LAST_GRAPH = None


@contextmanager
def locked_graph(timeout: float = 30.0):
    global LAST_GRAPH
    g = Graph()
    if SEED_GRAPH is not None:
        for t in SEED_GRAPH:
            g.add(t)
    try:
        yield g
    finally:
        LAST_GRAPH = g

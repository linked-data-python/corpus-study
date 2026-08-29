"""Validation driver for biokb__biokb_wfo__src_biokb_wfo_rdf_turtle.py__TurtleCreator_create_nodes_ttl.

create_nodes_ttl returns only a file path built from self.__ttls_folder --
comparing that return value alone would be a hollow green, since it says
nothing about the graph the region actually built (see context_shim.py:
get_empty_graph stashes the produced graph onto `self.produced_graph`
instead, because create_nodes_ttl calls it bare, not as
self.get_empty_graph()). TurtleCreator.__eq__ compares that graph by
isomorphism, so run_pair's own argument comparison (it compares every call
argument, `self` included, and `self` is args[0] here) becomes the real
oracle -- no need to read the ttl file back from disk.

`self` must be a FRESH object per side (unlike a region where the graph is a
separate, externally-passed argument): create_nodes_ttl mutates a graph it
reaches through `self`, so sharing one `self` between both calls would let
the second call's triples land in the same graph as the first's. The case
factory therefore builds a fresh TurtleCreator per side, from the same rows.

Four taxon rows exercise the stratum's two `if` guards independently (each
guard's `.add` is its own `+{ }`, never merged with the five unconditional
ones or with each other -- see meta.json):

  * parent_id and ipni both set    -- both guards fire
  * parent_id falsy (0), ipni None -- neither guard fires
  * only parent_id set
  * only ipni set
"""
import tempfile
from types import SimpleNamespace

from context_shim import TurtleCreator

from rdfeval.harness import run_pair


def _rows():
    return [
        SimpleNamespace(id=1, full_name="Taxon One", rank="species",
                         parent_id=10, ipni="12345", role="accepted"),
        SimpleNamespace(id=2, full_name="Taxon Two", rank="genus",
                         parent_id=0, ipni=None, role="synonym"),
        SimpleNamespace(id=3, full_name="Taxon Three", rank="family",
                         parent_id=30, ipni=None, role="accepted"),
        SimpleNamespace(id=4, full_name="Taxon Four", rank="order",
                         parent_id=0, ipni="99999", role="synonym"),
    ]


# Both sides write to the SAME directory: create_nodes_ttl's return value
# (the ttl path) is compared too, and the actual file content is never read
# back (the graph is compared directly, via TurtleCreator.produced_graph --
# see the module docstring), so a shared, one-off temp dir keeps that
# incidental return value identical on both sides without meaning anything.
_TTLS_DIR = tempfile.mkdtemp()


def factory():
    return ((TurtleCreator(_TTLS_DIR, _rows()),), {})


VERDICT = run_pair(
    __file__,
    entry="create_nodes_ttl",
    calls=[factory],
)

"""Validation driver for ScaDS__KGpipe__src_kgpipe_evaluation_aspects_semantic.py__DisjointDomainMetric_compute.

EXCLUDED (see meta.json): ``compute(self, kg, config, **kwargs)`` cannot run
outside the KGpipe package.  Two independent blockers, in the order Python
hits them:

  1. ``from ...common.models import KG, Data, DataFormat`` /
     ``from ..base import ...`` are package-relative imports that only
     resolve inside the ``kgpipe`` package -- restoring them faithfully
     means vendoring a chain of further internal modules (a pydantic
     ``Data`` model, ``kgpipe.common.graph.systemgraph``, ...), not a
     single self-contained binding.
  2. Even past that, ``ontology = OntologyUtil.load_ontology_from_graph(...)``
     and ``enrich_type_information(raw_graph, ontology)`` (the latter IS in
     the same source file, just outside the extracted window -- restorable)
     both need ``ontology.get_domain_range(...)``, which is real behaviour
     from ``kgcore.api.ontology.Ontology``.  ``kgcore`` is an external git
     dependency of this repository (`kgcore @ git+https://github.com/
     Vehnem/kgcore.git` in pyproject.toml), not vendored anywhere in the
     corpus, and reconstructing its domain/range resolution would mean
     inventing or importing a third repository's logic -- out of scope for
     a context shim.

``calls=`` below is what a working call would look like (a `kg`-shaped
stand-in exposing ``get_graph``/``get_ontology_graph``, `self` reduced to
its two touched attributes, ``config`` unused by the region's body), kept
for documentation even though ``original.py`` never reaches it: it already
fails at the ``from ...common.models import ...`` line above.
"""
from pathlib import Path
from types import SimpleNamespace

from rdfeval.harness import fixture_graph, run_pair

_FIXTURE = Path(__file__).resolve().parent / "fixture.ttl"


class _FakeKG:
    def __init__(self, graph, ontology_graph):
        self._graph = graph
        self._ontology_graph = ontology_graph

    def get_graph(self):
        return self._graph

    def get_ontology_graph(self):
        return self._ontology_graph


def _call():
    self_ = SimpleNamespace(name="disjoint_domain", aspect="semantic")
    kg = _FakeKG(fixture_graph(_FIXTURE), fixture_graph(_FIXTURE))
    return (self_, kg, None), {}


VERDICT = run_pair(
    __file__,
    entry='compute',
    fixture="fixture.ttl",
    calls=[_call],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

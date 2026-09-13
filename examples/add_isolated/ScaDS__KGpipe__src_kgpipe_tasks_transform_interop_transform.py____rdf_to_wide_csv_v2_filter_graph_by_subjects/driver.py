"""Validation driver for ScaDS__KGpipe__src_kgpipe_tasks_transform_interop_transform.py____rdf_to_wide_csv_v2_filter_graph_by_subjects.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdfeval.harness import run_pair

# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
def _fixture():
    from rdflib import Graph, URIRef, Literal
    g = Graph()
    s1, s2 = URIRef("http://ex.org/s1"), URIRef("http://ex.org/s2")
    p = URIRef("http://ex.org/p")
    g.add((s1, p, Literal("kept-1")))
    g.add((s1, p, Literal("kept-2")))
    g.add((s2, p, Literal("dropped")))
    subjects = {str(s1)}
    return ((g, subjects), {})


VERDICT = run_pair(
    __file__,
    entry='filter_graph_by_subjects',
    calls=[_fixture],
)

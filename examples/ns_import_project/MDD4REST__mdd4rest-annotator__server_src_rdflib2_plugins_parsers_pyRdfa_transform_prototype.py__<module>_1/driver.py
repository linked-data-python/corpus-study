"""Validation driver for
MDD4REST__mdd4rest-annotator__server_src_rdflib2_plugins_parsers_pyRdfa_transform_prototype.py__<module>_1.

``handle_prototypes(graph)`` mutates its argument in place and returns
``None``: the oracle is isomorphism of the graph AFTER the call, which
``run_pair``'s generic ``entry=``/``calls=`` path already gives us --
``_compare_value`` special-cases ``rdflib.Graph`` arguments and compares them
by isomorphism once the call has mutated them, on both sides.  Each fixture
below is a callable so ``run_pair`` builds a FRESH, independent graph per
side (mutable argument, see harness.py's own docstring on this point).

The graph exercises: a prototype (``ex:proto1``, typed ``rdfa:Pattern``)
copied into TWO different subjects (``ex:item1``, ``ex:item2``) -- multiple
matches, and repeated additions to the ``to_remove`` set that must still
dedupe to a single removal each; a ``rdfa:copy`` reference to something that
is NOT a prototype (``ex:notAPrototype`` has no ``rdf:type rdfa:Pattern``
triple) -- the neighbourhood that must NOT match, left untouched; and one
fully unrelated triple.
"""
from rdflib import Graph

from rdfeval.harness import run_pair

DATA = """
@prefix rdfa: <http://www.w3.org/ns/rdfa#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix ex: <http://example.org/> .

ex:item1 rdfa:copy ex:proto1 .
ex:proto1 rdf:type rdfa:Pattern .
ex:proto1 ex:hasColor "red" .
ex:proto1 ex:hasSize "M" .

# a second copy of the SAME prototype: multiplicity, and to_remove dedup
ex:item2 rdfa:copy ex:proto1 .

# neighbourhood that must NOT match: no rdf:type rdfa:Pattern on the target
ex:item3 rdfa:copy ex:notAPrototype .
ex:notAPrototype ex:hasColor "blue" .

# unrelated triple, must survive untouched
ex:other ex:unrelated "noise" .
"""


def build_graph():
    return Graph().parse(data=DATA, format="turtle")


VERDICT = run_pair(
    __file__,
    entry="handle_prototypes",
    calls=[
        lambda: ((build_graph(),), {}),
    ],
)

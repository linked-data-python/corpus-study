"""Validation driver for SwissDataScienceCenter__calamus__calamus_fields.py__Namespace___getattr__.

`__getattr__(self, name)` is a method extracted as a free function with
`self` as an explicit, unannotated parameter (same convention as the
Terramorpha__minergym and IndustryFusion RdfUtils.get_all_subreferences
precedents elsewhere in this stratum): `self` needs `.namespace` (a str)
and `.ontology` (None, or an rdflib Graph) -- exactly the two attributes
`calamus.fields.Namespace` carries, and `.namespace` needs `str(self)` to
return it (calamus/fields.py: `Namespace.__str__`), because
`IRIReference.__str__` interpolates `self.namespace` (the OUTER namespace
object) through `str.format`, which falls back to `str()`. `_NS` below
reproduces exactly that much -- not `Namespace.__init__`'s ontology-file
parsing, which this region never calls.

Two calls, both avoiding the branch that raises (see meta.json: run_pair
treats ANY exception from either side as a hard error, not a value to
compare, so a case built to raise would not exercise the comparison at
all):

  * `ontology=None` -- skips the query entirely, exercises the "no
    ontology" path.
  * `ontology=<a Graph declaring the property as an owl:DatatypeProperty>`
    -- exercises the ASK + initBindings branch with a query that succeeds
    (so no ValueError), i.e. the one rdflib idiom this stratum targets.

meta.classification is not-expressible (see translated.ldpy): the region
was left as plain rdflib/Python on both sides, so this driver's real job is
confirming that restoring the missing bindings (`IRIReference`, the
`self`-like object) did not itself introduce a difference, and that the
check can actually fail (see the anti-hollow-green note in meta.json) --
not exercising any island.
"""
from rdflib import Graph, URIRef
from rdflib.namespace import OWL, RDF

from rdfeval.harness import run_pair


class _NS:
    """Minimal stand-in for calamus.fields.Namespace (see module docstring):
    only the two attributes and the __str__ that __getattr__ itself reads."""

    def __init__(self, namespace, ontology=None):
        self.namespace = namespace
        self.ontology = ontology

    def __str__(self):
        return self.namespace


def _ontology_graph():
    g = Graph()
    g.add((URIRef("http://example.org/ns#knows"), RDF.type, OWL.ObjectProperty))
    return g


# Built once and shared by both sides, like the Terramorpha__minergym
# precedent: the region only reads (and only ever calls str()/format() on
# `self`, never mutates it), so there is no risk a side's evaluation leaks
# into the other's, and run_pair also compares each argument after the call
# to catch such mutation -- a FRESH `_NS` per side would spuriously
# "differ" since it defines no `__eq__`, only identity.
_no_ontology = _NS("http://example.org/ns#")
_with_ontology = _NS("http://example.org/ns#", ontology=_ontology_graph())

VERDICT = run_pair(
    __file__,
    entry="__getattr__",
    calls=[
        ((_no_ontology, "unchecked"), {}),  # ontology=None: no query at all
        ((_with_ontology, "knows"), {}),  # ASK + initBindings branch, query succeeds
    ],
)

"""Validation driver for Harold-Solbrig__funowl__funowl_annotations.py__Annotatable_TANN.

TANN takes `self` (an Annotatable) and mutates the `g` argument in place,
returning None -- so the oracle is the isomorphism of `g` after the call,
compared as a positional argument (rdfeval.harness compares every call
argument, and a Graph argument is compared by isomorphism like a return
value would be).

`self` and `subj` are built ONCE per case and closed over, so both sides
receive the SAME object (not a fresh, unequal copy) -- only `g` is fresh per
side, which matters because `self`/`subj` carry no `__eq__` of their own
(see context_shim.py) and comparing two distinct instances by identity would
report a spurious diff that has nothing to do with the translation.

Three cases:

  * `subj_not_a_tuple`   -- `isinstance(subj, Tuple)` is False, the whole
    reification block (the stratum's site: 4 g.add on the same BNode `x`,
    merged into one `+{ ; ; ; }`) is skipped entirely -- only the per-
    annotation loop runs (2 annotations sharing `subj`, left as plain
    `g.add(t)`, see meta.json for why).
  * `subj_tuple_one_annotation` -- triggers the reification block (the
    stratum's site) with exactly one following annotation.
  * `subj_tuple_two_annotations` -- same, with two annotations, so the loop
    below the reified block also runs twice on the same reified subject `x`.

Every Annotation built here has annotations=[] (no further nesting): TANN's
own recursive `annotation.TANN(g, t)` call then hits `if self.annotations:`
False and returns immediately, on both sides, so the shim's Annotation.TANN
(a guard, not a real implementation -- see context_shim.py) is never
actually exercised by these fixtures.
"""
from rdflib import Graph, Literal, URIRef
from rdflib.namespace import OWL

from context_shim import Annotatable, Annotation

from rdfeval.harness import run_pair

AP1 = URIRef("http://example.org/onto#createdBy")
AP2 = URIRef("http://example.org/onto#comment")
SRC = URIRef("http://example.org/onto#Widget")
PROP = URIRef("http://example.org/onto#hasPart")
TARGET_IRI = URIRef("http://example.org/onto#Cog")


def case(subj, annotations):
    # Built ONCE, outside the closure: `factory()` runs twice (once per
    # side), and self_obj must be the SAME object both times -- see the
    # module docstring on why a freshly-rebuilt self would spuriously fail
    # the argument comparison.
    self_obj = Annotatable(annotations, annotation_type=OWL.Axiom)

    def factory():
        return ((self_obj, Graph(), subj), {})
    return factory


VERDICT = run_pair(
    __file__,
    entry="TANN",
    calls=[
        # subj is a plain URIRef: the reification site (this stratum's `;`
        # merge) is skipped; two annotations still share `subj` in the loop.
        case(SRC, [Annotation(AP1, Literal("Ana")), Annotation(AP2, Literal("v1"))]),
        # subj is a triple: reification fires, one annotation follows.
        case((SRC, PROP, TARGET_IRI), [Annotation(AP1, Literal("Ana"))]),
        # subj is a triple, two annotations follow the reified subject.
        case((SRC, PROP, TARGET_IRI),
             [Annotation(AP1, Literal("Ana")), Annotation(AP2, Literal("v1"))]),
    ],
)

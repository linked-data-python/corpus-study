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

Every Annotation built here has annotations=[] (no further nesting), so the
shim's Annotation.TANN (a guard, not a real implementation -- see
context_shim.py) is never reached.  The recursion `annotation.TANN(g, t)` is
nevertheless proven: the annotations of the BNode cases below are
`MarkedAnnotation`s, a driver-local subclass whose TANN adds one marker
triple `(t[0], EX.recursed, t[2])` to `g`.  If the region stopped calling
`annotation.TANN(g, t)`, or called it with another graph or another triple,
the marker would be missing or different and the isomorphism would fail.

Four cases then exercise `clone_subgraph` on BNodes, which is what the
interpolated `{clone_subgraph(g, subj[0]) if USE_BNODE_COPIES else subj[0]}`
holes do and what distinguishes the translation from a plain rewrite (in the
real repository the elements of the annotated triple come from `.to_rdf(g)`
and are often BNodes):

  * `bnode_chain` -- subj = (b, hasPart, d) where b -> c is a chain of
    BNodes in `g` carrying triples: the source must be cloned along with its
    BNode subgraph.
  * `bnode_self_loop` -- subj = (b, p, b): source and target are the same
    BNode with a self-referential triple (each clone gets its own copy).
  * `bnode_self_loop_with_neighbourhood` -- same, plus a triple of another
    BNode pointing INTO b, which must not be cloned.
  * `bnode_target_literal` -- subj = (b, p, Literal): the target is not a
    BNode and must be left untouched while the source is cloned; also a
    triple whose source is a URIRef and whose target is a BNode.
"""
from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import OWL

from context_shim import Annotatable, Annotation

from rdfeval.harness import run_pair

AP1 = URIRef("http://example.org/onto#createdBy")
AP2 = URIRef("http://example.org/onto#comment")
SRC = URIRef("http://example.org/onto#Widget")
PROP = URIRef("http://example.org/onto#hasPart")
TARGET_IRI = URIRef("http://example.org/onto#Cog")


EX_RECURSED = URIRef("http://example.org/onto#recursed")


class MarkedAnnotation(Annotation):
    """Annotation whose TANN leaves a witness in `g` that it was called,
    with which graph and which triple (see module docstring)."""

    def TANN(self, g, subj):
        g.add((subj[0], EX_RECURSED, subj[2]))


def bnode_case(build_graph, subj, annotations):
    """Like `case`, but the Graph is pre-populated by `build_graph(g)`
    (BNode neighbourhood that clone_subgraph walks); `subj` and its BNodes
    are shared by both sides, only the Graph is fresh per call."""
    self_obj = Annotatable(annotations, annotation_type=OWL.Axiom)

    def factory():
        g = Graph()
        build_graph(g)
        return ((self_obj, g, subj), {})
    return factory


B1, B2, B3 = BNode(), BNode(), BNode()
HAS_PART = URIRef("http://example.org/onto#hasPart")
LABEL = URIRef("http://example.org/onto#label")
LINK = URIRef("http://example.org/onto#link")


def _chain(g):
    g.add((B1, LABEL, Literal("b1")))
    g.add((B1, LINK, B2))
    g.add((B2, LABEL, Literal("b2")))
    g.add((B2, LINK, TARGET_IRI))


def _self_loop(g):
    g.add((B1, LABEL, Literal("loop")))
    g.add((B1, LINK, B1))


def _self_loop_neighbourhood(g):
    _self_loop(g)
    g.add((B1, LINK, B2))
    g.add((B2, LABEL, Literal("child")))
    g.add((B3, LINK, B1))          # points INTO b1: must not be cloned
    g.add((B3, LABEL, Literal("parent")))


def _source_and_literal(g):
    g.add((B1, LABEL, Literal("b1")))
    g.add((B1, LINK, B2))
    g.add((B2, LABEL, Literal("b2")))


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
        # BNode elements carrying triples in g; recursion witnessed by
        # MarkedAnnotation.
        bnode_case(_chain, (B1, HAS_PART, TARGET_IRI),
                   [MarkedAnnotation(AP1, Literal("Ana"))]),
        bnode_case(_chain, (SRC, HAS_PART, B1),
                   [MarkedAnnotation(AP1, Literal("Ana")),
                    MarkedAnnotation(AP2, Literal("v1"))]),
        bnode_case(_chain, (B1, HAS_PART, B2),
                   [MarkedAnnotation(AP1, Literal("Ana"))]),
        bnode_case(_self_loop, (B1, PROP, B1),
                   [MarkedAnnotation(AP1, Literal("Ana"))]),
        bnode_case(_self_loop_neighbourhood, (B1, PROP, B1),
                   [MarkedAnnotation(AP1, Literal("Ana"))]),
        bnode_case(_source_and_literal, (B1, PROP, Literal("lit")),
                   [MarkedAnnotation(AP1, Literal("Ana"))]),
        # subj is a BNode (not a tuple): no reification, no cloning, the
        # recursion is still witnessed.
        bnode_case(_chain, B1, [MarkedAnnotation(AP1, Literal("Ana"))]),
    ],
)

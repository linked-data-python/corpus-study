"""Validation driver for aigora-de__rdf-construct__src_rdf_construct_shacl_converters.py__PropertyConstraint_to_rdf.

`to_rdf(self, shapes_graph)` is a method extracted with an explicit `self`
first parameter and an explicit `shapes_graph` parameter (unlike a
`self.graph`-style attribute region, the receiver is already a normal
argument). `self` is `context_shim.PropertyConstraint`, a plain `@dataclass`
with the library's own generated `__eq__` comparing field values -- so the
driver's per-argument comparison (run_pair compares `args_o[0]` against
`args_t[0]` after the call) reports true structural equality between the two
sides' independently-built instances with no custom `__eq__` needed, unlike
a region reached through `self.<attr>` (see the sibling coercion_datatype
region on Concept in this same batch, which does need one).

CALL_1 -- every field set, so every branch of the twelve `if`/`if ... is not
None` guards fires once: node_class/datatype/node_kind (URIRef, direct
pass-through, no coercion), min_count/max_count/order (int -> Literal with
no explicit datatype, i.e. rdflib's own int->xsd:integer inference),
name/description/pattern (str -> Literal with no datatype, i.e. a plain
literal), in_values with two items (one URIRef, one Literal) exercising
_create_rdf_list (untouched: it sits just past the extracted region, see
context_shim.py), and min_inclusive/max_inclusive as already-constructed
Literal instances (pass-through, not re-wrapped).

CALL_2 -- only `path` set (the one required field), every optional field at
its dataclass default (None / empty list): every guarded branch is skipped,
so only the unconditional `sh:path` triple is written -- the zero-optional
edge.
"""
from rdflib import Graph, Literal, URIRef, XSD

from context_shim import PropertyConstraint, SH
from rdfeval.harness import run_pair


def _case_full():
    self = PropertyConstraint(
        path=URIRef("http://example.org/prop"),
        node_class=URIRef("http://example.org/ClassA"),
        datatype=XSD.string,
        min_count=1,
        max_count=3,
        node_kind=SH.IRI,
        name="Label",
        description="A description",
        in_values=[URIRef("http://example.org/v1"), Literal("v2")],
        pattern="^[a-z]+$",
        min_inclusive=Literal(0),
        max_inclusive=Literal(10),
        order=2,
    )
    return ((self, Graph()), {})


def _case_minimal():
    self = PropertyConstraint(path=URIRef("http://example.org/prop2"))
    return ((self, Graph()), {})


VERDICT = run_pair(
    __file__,
    entry='to_rdf',
    calls=[_case_full, _case_minimal],
)

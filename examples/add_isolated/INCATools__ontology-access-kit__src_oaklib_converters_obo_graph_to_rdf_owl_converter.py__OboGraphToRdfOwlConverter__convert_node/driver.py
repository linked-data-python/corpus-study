"""Validation driver for INCATools__ontology-access-kit__src_oaklib_converters_obo_graph_to_rdf_owl_converter.py__OboGraphToRdfOwlConverter__convert_node.

Establishes semantic equivalence of original.py and translated.ldpy: each
case calls `_convert_node(self, node, Graph())` on both sides; run_pair
compares the returned graph and the mutated `target` by isomorphism, and
`self` by equality.

The first six cases cover the six island branches (owl:Class with and
without a type, the three property types, owl:NamedIndividual) and the
label island.  The cases after them were added by the mutation audit of
2026-10-30, each for a mutant of the guards around the islands that the
first six left alive; every input is one the repository's datamodel admits
(oaklib/datamodels/obograph.py: `Node.type` is an Optional[str],
`propertyType` Optional, `lbl` Optional[str]):

  * type == "" -- falsy but not None: `not source.type` takes the
    owl:Class branch, `source.type is None` would raise;
  * type == "PROPERTY" with no propertyType -- the common case of an
    obographs property node: no triple at all (forcing the DATA guard to
    True would add owl:DatatypeProperty);
  * an unknown type -- the `raise ValueError` branch, compared by type and
    message (forcing the INDIVIDUAL guard to True, or deleting the raise,
    would answer with a graph);
  * lbl == "" -- `if source.lbl:` writes no label, `is not None` would
    write an empty one;
  * a node with a Meta -- the `self._convert_meta(...)` call.  The shim's
    `_convert_meta` is a no-op, so a recorder (RecordingConverter, below,
    identical for both sides) logs each call, and `self` -- compared by
    run_pair as call[i].arg[0] -- is equal only if both sides made the same
    calls with the same arguments.

After run_pair, a second phase runs every case again and compares the
prefix bindings of `target`: the repository serialises that graph
(OboGraphToRdfOwlConverter.dump, g.serialize), so `@graph target` must not
replace a binding the original's graph has (it may add the block's own,
record ldpy/027).

Equivalent mutant, not counted: `if source.meta:` -> `is not None` (a Meta
dataclass is always truthy).
"""
import contextlib
import io
from pathlib import Path

from rdfeval.harness import _emit, _exec_ldpy, _exec_python, run_pair
from context_shim import Converter, Meta, Node, PropertyTypeEnum
from rdflib import Graph

HERE = Path(__file__).resolve().parent


class RecordingConverter(Converter):
    """Converter whose `_convert_meta` records its calls (same on both sides)."""

    def __init__(self):
        self.meta_calls = []

    def _convert_meta(self, uri, source, target):
        self.meta_calls.append((uri, source, len(target)))
        return target

    def __eq__(self, other):
        return (isinstance(other, RecordingConverter)
                and self.meta_calls == other.meta_calls)

    def __hash__(self):
        return hash(RecordingConverter)

    def __repr__(self):
        return f"RecordingConverter({self.meta_calls!r})"


def _case(node, converter=Converter):
    def make():
        return ((converter(), node, Graph()), {})
    return make


CALLS = [
    # not source.type -> owl:Class, plus a plain-literal label
    _case(Node(id="obo:CL_0000000", lbl="cell", type=None, meta=None)),
    # source.type == "CLASS" (explicit), no label
    _case(Node(id="obo:CL_0000001", lbl=None, type="CLASS", meta=None)),
    # PROPERTY / OBJECT
    _case(Node(id="obo:RO_0002131", lbl="overlaps",
                type="PROPERTY", propertyType=PropertyTypeEnum.OBJECT,
                meta=None)),
    # PROPERTY / ANNOTATION
    _case(Node(id="obo:IAO_0000115", lbl=None,
                type="PROPERTY", propertyType=PropertyTypeEnum.ANNOTATION,
                meta=None)),
    # PROPERTY / DATA
    _case(Node(id="obo:hasWeight", lbl=None,
                type="PROPERTY", propertyType=PropertyTypeEnum.DATA,
                meta=None)),
    # INDIVIDUAL
    _case(Node(id="obo:individual_1", lbl="Alice",
                type="INDIVIDUAL", meta=None)),
    # type == "": falsy, not None -> owl:Class
    _case(Node(id="obo:CL_0000002", lbl="cell part", type="", meta=None)),
    # PROPERTY without a propertyType -> no type triple, label only
    _case(Node(id="obo:BFO_0000050", lbl="part of",
                type="PROPERTY", propertyType=None, meta=None)),
    # unknown type -> ValueError("Unknown node type: OTHER")
    _case(Node(id="obo:X_0000001", lbl="x", type="OTHER", meta=None)),
    # lbl == "" -> no label
    _case(Node(id="obo:CL_0000003", lbl="", type="CLASS", meta=None)),
    # a Meta -> one _convert_meta call, recorded on self
    _case(Node(id="obo:CL_0000004", lbl="neuron", type="CLASS",
                meta=Meta(definition="A nerve cell.")),
          converter=RecordingConverter),
    # no Meta, recorder present -> no _convert_meta call
    _case(Node(id="obo:CL_0000005", lbl="glia", type="CLASS", meta=None),
          converter=RecordingConverter),
]

with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(
        __file__,
        entry='_convert_node',
        calls=CALLS,
    )

if not VERDICT.get("error"):
    extra = []
    fo = _exec_python(HERE / "original.py")[0]["_convert_node"]
    ft = _exec_ldpy(HERE / "translated.ldpy")[0]["_convert_node"]
    for i, make in enumerate(CALLS):
        (self_o, node, go), _ = make()
        (self_t, _node, gt), _ = make()
        for f, s, g in ((fo, self_o, go), (ft, self_t, gt)):
            try:
                f(s, node, g)
            except Exception:                         # noqa: BLE001 - compared above
                pass
        lost = sorted({(p, str(u)) for p, u in go.namespaces()}
                      - {(p, str(u)) for p, u in gt.namespaces()})
        if lost:
            extra.append(f"call[{i}]: prefix bindings of the original lost "
                         f"in the translation: {lost}")
    VERDICT["method"] += " + target bindings"
    VERDICT["diffs"] = VERDICT["diffs"] + extra
    VERDICT["equivalent"] = not VERDICT["diffs"]

_emit(VERDICT)

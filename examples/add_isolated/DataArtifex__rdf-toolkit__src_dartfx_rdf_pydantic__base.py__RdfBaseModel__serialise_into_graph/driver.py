"""Validation driver for DataArtifex__rdf-toolkit__src_dartfx_rdf_pydantic__base.py__RdfBaseModel__serialise_into_graph.

`_serialise_into_graph` is a method (`self` is an explicit first parameter):
both original.py and translated.ldpy carry an identical demo(model, graph)
harness (see meta.json and context_shim.py) that calls
`_serialise_into_graph` on a `context_shim.RdfBaseModelStub` instance and
returns the graph it wrote into -- so the driver compares the graphs demo()
returns, not `model` itself (comparing the stub by identity would report a
spurious difference on every call: each side builds its own instance).

CALL_1 -- one model exercising every branch the region takes:
  - rdf_type set -> the `a` triple;
  - a LangStringList field with two entries (one tagged "fr", one untagged)
    -> the fast-path loop, two language-literal triples;
  - a scalar (non-list) field with a plain string value -> the
    is_list=False path, one plain-literal triple;
  - a list field with two string items -> the is_list=True path, two triples;
  - a field with no RdfProperty metadata at all -> `if prop is None:
    continue` (contributes nothing);
  - a field whose value is None -> `if value is None: continue`
    (contributes nothing);
  - a list field containing a None item alongside real ones -> `if item is
    None: continue` inside the inner loop (only the non-None item is
    written).

CALL_2 -- rdf_type is None (no `a` triple) and every RdfProperty-bearing
field's value is None: the whole loop body contributes nothing beyond the
subject existing implicitly (an empty graph, since `graph.bind` doesn't add
triples) -- the zero-triples edge of the region.
"""
from rdfeval.harness import run_pair
from rdflib import Graph, URIRef
from context_shim import LangString, LangStringList, RdfBaseModelStub, RdfProperty, FieldInfo

SUBJECT = URIRef("http://ex/s1")

MODEL_1_FIELDS = {
    "label": FieldInfo(LangStringList, metadata=(RdfProperty("http://ex/label"),)),
    "note": FieldInfo(str, metadata=(RdfProperty("http://ex/note"),)),
    "tags": FieldInfo(list[str], metadata=(RdfProperty("http://ex/tag"),)),
    "internal": FieldInfo(str, metadata=()),
    "empty": FieldInfo(str, metadata=(RdfProperty("http://ex/empty"),)),
}


class Model1(RdfBaseModelStub):
    rdf_type = "http://ex/Person"
    model_fields = MODEL_1_FIELDS


def _model_1():
    return Model1(
        SUBJECT,
        label=LangStringList([LangString("Bonjour", "fr"), LangString("Hello", None)]),
        note="a single note",
        tags=["a", "b", None],
        internal="ignored (no RdfProperty)",
        empty=None,
    )


MODEL_2_FIELDS = {
    "note": FieldInfo(str, metadata=(RdfProperty("http://ex/note"),)),
}


class Model2(RdfBaseModelStub):
    rdf_type = None
    model_fields = MODEL_2_FIELDS


def _model_2():
    return Model2(SUBJECT, note=None)


VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        (lambda: ((_model_1(), Graph()), {})),
        (lambda: ((_model_2(), Graph()), {})),
    ],
)

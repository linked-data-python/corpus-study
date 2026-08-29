# Extracted from eccenca/cmem-plugin-pyshacl@faf59e81de : cmem_plugin_pyshacl/plugin_pyshacl.py
# region: ShaclValidation.add_shui_conforms_val (lines 429-444, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import (
    PROV,
    RDF,
    RDFS,
    SH,
    SKOS,
    XSD,
    BNode,
    Graph,
    Literal,
    Namespace,
    URIRef,
)

def add_shui_conforms_val(
    self, validation_graph: Graph, validation_result_uris: list, focus_nodes: list
) -> Graph:
    """Add shui conforms flag"""
    self.log.info("Adding shui:conforms flags to validation graph")
    itr = focus_nodes or validation_result_uris
    for i in itr:
        subj = i if focus_nodes else validation_graph.value(subject=i, predicate=SH.focusNode)
        validation_graph.add(
            (
                subj,
                URIRef("https://vocab.eccenca.com/shui/conforms"),
                Literal(False, datatype=XSD.boolean),
            )
        )
    return validation_graph

# --- Test harness only (see meta.json) — identical in original.py and
# translated.ldpy except for the one line that mirrors the region's own
# read construction. `self.log.info(...)` is the only use of `self` in the
# region, hence the tiny stub. `demo(mode, ...)` has two modes:
#   "mutate" — calls the real, unmodified region (covers several solutions
#     across two result URIs, and the focus_nodes-provided branch that
#     never reads at all);
#   "read"   — evaluates the region's own read expression in isolation,
#     because the region's `.add()` call cannot tolerate a None subject
#     (verified: rdflib raises `AssertionError` on `add((None, ...))`), so
#     the zero-solution case cannot be driven through "mutate" without
#     crashing both sides before any comparison happens.
class _SelfStub:
    class _Log:
        def info(self, *args, **kwargs):
            pass
    log = _Log()

def demo(mode, validation_graph, a, b=None):
    if mode == "mutate":
        return add_shui_conforms_val(_SelfStub(), validation_graph, a, b)
    return validation_graph.value(subject=a, predicate=SH.focusNode)

"""Validation driver for beyonai__ByDC__…__GraphBuilder_add_entity_mapping.

Establishes semantic equivalence of original.py and translated.ldpy.
`demo` is the identical harness both files carry (see meta.json):
add_entity_mapping is a method body lifted out of its class, so `demo`
builds the minimal `self` (context_shim.GraphBuilderStub) and returns the
graph add_entity_mapping(self, ...) writes -- the region's only
RDF-observable effect (meta.oracle: isomorphism).

Three calls: (1) a code needing `_safe_xml_id`'s substitution (a dot and a
dash are not `\\w`) with two mapping_refs, exercising the loop over more
than one ref; (2) mapping_refs=None, exercising the `if mapping_refs:`
False branch (no third triple at all, not even zero iterations of a loop
that would still run); (3) an empty-string object_desc, still passed
through unconditionally to _add_literal.

Prefix bindings, compared on top of run_pair's isomorphism: the repository
serialises this very graph to RDF/XML (renderers/ontology.py:181, reached
from the only call site, ontology.py:593), and GraphBuilder.__init__ binds
the default prefix "" to its namespace on purpose ("命名空间对齐现有 OWL
格式（xml:base + 默认 ns）", graph_builder.py:9). `@graph` binds the block's
prefixes into the designated graph (record ldpy/027); a prefix of another
name for the same namespace would REPLACE the "" binding (rdflib's bind
overrides), and the RDF/XML would change from the default namespace to
`ns:`. So, for every call, each binding of the original's graph must be in
the translation's; extra bindings are tolerated.
"""
import contextlib
import io
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

CALLS = [
    (("tbl.order-2", "Order Table", "订单表",
      ["prop_code_mapping", "prop_status_mapping"]), {}),
    (("tbl_customer", "Customer Table", "客户表", None), {}),
    (("tbl_empty", "Empty Table", "", []), {}),
]

ex_dir = Path(__file__).resolve().parent
with contextlib.redirect_stderr(io.StringIO()):       # this driver emits
    VERDICT = run_pair(__file__, entry='demo', calls=CALLS)

try:
    ns_o, _ = harness._exec_python(ex_dir / "original.py")
    ns_t, _ = harness._exec_ldpy(ex_dir / "translated.ldpy")
    for i, (args, kwargs) in enumerate(CALLS):
        go = ns_o["demo"](*args, **kwargs)
        gt = ns_t["demo"](*args, **kwargs)
        lost = set(go.namespaces()) - set(gt.namespaces())
        if lost:
            VERDICT["diffs"].append(
                f"call[{i}]: prefix bindings lost {sorted(lost)}")
except Exception:
    import traceback
    VERDICT["error"] = traceback.format_exc(limit=8)
VERDICT["method"] = f"{VERDICT.get('method')} + prefix bindings"
VERDICT["equivalent"] = not VERDICT["diffs"] and not VERDICT.get("error")
harness._emit(VERDICT)

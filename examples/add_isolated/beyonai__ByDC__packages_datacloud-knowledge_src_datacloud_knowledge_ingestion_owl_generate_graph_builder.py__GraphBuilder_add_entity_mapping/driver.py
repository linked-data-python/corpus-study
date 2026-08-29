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
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='demo',
    calls=[
        (("tbl.order-2", "Order Table", "订单表",
          ["prop_code_mapping", "prop_status_mapping"]), {}),
        (("tbl_customer", "Customer Table", "客户表", None), {}),
        (("tbl_empty", "Empty Table", "", []), {}),
    ],
)

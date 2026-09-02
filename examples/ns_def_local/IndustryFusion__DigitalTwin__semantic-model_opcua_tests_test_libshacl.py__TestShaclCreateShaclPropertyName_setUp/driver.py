"""Validation driver for IndustryFusion__DigitalTwin__semantic-model_opcua_tests_test_libshacl.py__TestShaclCreateShaclPropertyName_setUp.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
from rdflib import Graph
from rdfeval.harness import run_pair, graphs_isomorphic


class _FakeSelf:
    """Stands in for the TestCase instance `setUp(self)` mutates.

    Plain ``==`` on a SimpleNamespace would compare a nested ``Graph``
    attribute (``data_graph``, and ``shacl.data_graph`` once wrapped) by
    ``Graph.identifier`` -- a fresh BNode per instance -- so two runs of the
    *same* code would spuriously disagree.  This ``__eq__`` recurses through
    plain attributes and reduces any ``Graph`` it meets to isomorphism.
    """

    def __eq__(self, other):
        if not isinstance(other, _FakeSelf):
            return NotImplemented
        keys = set(vars(self)) | set(vars(other))
        return all(_eq(getattr(self, k, _MISSING), getattr(other, k, _MISSING))
                    for k in keys)


_MISSING = object()


def _eq(a, b):
    if isinstance(a, Graph) and isinstance(b, Graph):
        return graphs_isomorphic(a, b)
    if isinstance(a, _FakeSelf) or isinstance(b, _FakeSelf):
        return a == b
    if isinstance(a, (str, bytes)) or isinstance(b, (str, bytes)):
        # Namespace/URIRef are str subclasses: their value lives in the str
        # payload, not in per-instance __dict__ (usually empty/absent), so
        # they must compare by value, never by attribute recursion.
        return a == b
    if hasattr(a, "__dict__") and hasattr(b, "__dict__") \
            and type(a) is type(b) and type(a).__module__ != "builtins":
        keys = set(vars(a)) | set(vars(b))
        return all(_eq(getattr(a, k, _MISSING), getattr(b, k, _MISSING))
                    for k in keys)
    return a == b


# setUp(self) only ever assigns attributes on `self`; a fresh _FakeSelf
# stands in for the TestCase instance so each side gets its own object to
# mutate, and its __eq__ is what lets the harness compare the resulting
# attributes -- namespace_prefix, basens, opcuans, data_graph, shacl (whose
# own data_graph/namespace_prefix/basens/opcuans must also agree) -- across
# the two runs, without a fresh Graph()'s BNode identifier causing a false
# mismatch.
VERDICT = run_pair(
    __file__,
    entry='setUp',
    calls=[lambda: ((_FakeSelf(),), {})],
)

"""Validation driver for MaxBerktoldRWTH__BRICKbuilder__src_app_ifc_populate_window.py__IfcBrickAnnotator_rebuild_output_graph.

This region CONSTRUCTS a graph (self.output_graph), so the oracle is RDF
isomorphism, not value equality (design record corpus/405). It mutates the
`self` it is called on rather than returning anything, so the harness's
per-argument comparison (`run_pair(..., entry=..., calls=...)`) is what
proves equivalence: it compares `self` after calling original.py's
`rebuild_output_graph` against `self` after calling translated.ldpy's.

`self` needs `.output_graph` (created by the region itself), `.BRICK`,
`.REF` (real Namespace objects -- set up in the sibling region
IfcBrickAnnotator.load_brick_schema, reproduced here with their real
defaults: https://brickschema.org/schema/Brick# and
https://brickschema.org/schema/Brick/ref#), `.settings` (a QSettings
stand-in exposing just `.value(key, default)`), and `.annotations_registry`
(the dict of dicts the region iterates). No context_shim.py is needed: the
region's own body references only `self.*` and rdflib names already
imported in original.py -- nothing else is missing.

Plain `==` on a SimpleNamespace-like stand-in would compare `.output_graph`
(a fresh Graph()) by identity (always "different") and `.BRICK`/`.REF`
(Namespace, a str subclass) by recursing into `vars()` -- empty, so any two
Namespaces would look "equal" regardless of their IRI (the ANTI-VERT-CREUX
pitfall AGENT_BATCH.md names explicitly). `_FakeSelf.__eq__` below is the
same comparator already used by the sibling driver in this stratum,
IndustryFusion__DigitalTwin__..._TestShaclCreateShaclPropertyName_setUp:
`Graph` attributes compare by `graphs_isomorphic()`, `str` subclasses
(Namespace/URIRef/Literal) compare by value, and everything else recurses
through `vars()`. `run_pair`'s own comparison machinery falls through to
plain `==` for an object that is none of Graph/BNode/dict/list/tuple/set,
so defining `__eq__` on `_FakeSelf` is enough -- no need to touch
rdfeval/harness.py.
"""
from rdflib import Graph, Namespace

from rdfeval.harness import run_pair, graphs_isomorphic

_MISSING = object()


def _eq(a, b):
    if isinstance(a, Graph) and isinstance(b, Graph):
        return graphs_isomorphic(a, b)
    if isinstance(a, _FakeSelf) or isinstance(b, _FakeSelf):
        return a == b
    if isinstance(a, (str, bytes)) or isinstance(b, (str, bytes)):
        return a == b
    if hasattr(a, "__dict__") and hasattr(b, "__dict__") \
            and type(a) is type(b) and type(a).__module__ != "builtins":
        keys = set(vars(a)) | set(vars(b))
        return all(_eq(getattr(a, k, _MISSING), getattr(b, k, _MISSING))
                   for k in keys)
    return a == b


class _Settings:
    """Stands in for the QSettings the region reads through .value(key, default)."""

    def __init__(self, data):
        self._data = dict(data)

    def value(self, key, default=None):
        return self._data.get(key, default)

    def __eq__(self, other):
        return isinstance(other, _Settings) and self._data == other._data


def _annotations_registry():
    # Three rows: a full one with a BACnet point (exercises the fused
    # bacnet_bnode block and its typed/plain literals), one missing
    # ifc_type (exercises the "IfcSensor" default) and bacnet_name
    # (exercises the `if data.raw.get("bacnet_name"):` guard being False --
    # must NOT leave stray bindings from a previous row's ?bacnet_name), and
    # a second full one with different bacnet_type munging
    # ("AnalogValue" -> "analog-value") so the loop is proven to run more
    # than once without state leaking between rows.
    return {
        "eq1": {
            "eq_guid": "EQ001", "ifc_type": "IfcSensor",
            "point_id": "PT001", "point_type": "Sensor",
            "bacnet_name": "Zone Temp", "bacnet_type": "AnalogInput",
            "bacnet_instance": 3,
        },
        "eq2": {
            "eq_guid": "EQ002",
            "point_id": "PT002", "point_type": "Setpoint",
        },
        "eq3": {
            "eq_guid": "EQ003", "ifc_type": "IfcActuator",
            "point_id": "PT003", "point_type": "Command",
            "bacnet_name": "Damper Cmd", "bacnet_type": "AnalogValue",
            "bacnet_instance": 7,
        },
    }


class _FakeSelf:
    """Stands in for the IfcBrickAnnotator instance `rebuild_output_graph(self)` mutates."""

    def __init__(self):
        self.settings = _Settings({
            # deliberately WITHOUT a trailing '#'/'/', so the region's own
            # `if not str(base_inst).endswith(('#', '/')): base_inst += '#'`
            # is exercised identically on both sides.
            "ns_inst": "http://example.org/testproj",
        })
        self.BRICK = Namespace("https://brickschema.org/schema/Brick#")
        self.REF = Namespace("https://brickschema.org/schema/Brick/ref#")
        self.annotations_registry = _annotations_registry()

    def __eq__(self, other):
        if not isinstance(other, _FakeSelf):
            return NotImplemented
        keys = set(vars(self)) | set(vars(other))
        return all(_eq(getattr(self, k, _MISSING), getattr(other, k, _MISSING))
                   for k in keys)


VERDICT = run_pair(
    __file__,
    entry="rebuild_output_graph",
    calls=[lambda: ((_FakeSelf(),), {})],
)

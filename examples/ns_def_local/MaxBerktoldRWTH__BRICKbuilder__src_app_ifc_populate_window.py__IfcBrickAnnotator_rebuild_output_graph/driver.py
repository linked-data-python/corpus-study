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

PREFIX BINDINGS.  Graph isomorphism does not see prefix bindings, yet the
repository reads them back (`send_graph_to_brickbuilder` serialises
`output_graph` and calls `namespaces()`).  The original makes seven
`output_graph.bind(prefix, ns)` calls; the translation replaces them with
`@prefix ... as ...` declarations followed by `@graph self.output_graph`.
So `_eq` compares, for two graphs, their isomorphism AND the bindings
(`_bindings_ok`): every (prefix, namespace) pair the ORIGINAL graph binds
must be bound identically by the translated one.  The check is one-sided on
purpose: the translated graph may carry extra bindings (rdflib's default
bindings, or any that `@graph` adds), and that is tolerated.  The left
operand of `==` is the original side (the harness compares `original ==
translated`).  Because rdflib's default `Graph()` already binds `brick` to
the real Brick IRI, the first call alone could not tell a missing
`@prefix brick:` apart; the second call therefore gives `self.BRICK`,
`self.REF`, `ns_ifc` and `ns_inst` values that differ from every default.

CALLS.
  0. the original three-row registry (see `_annotations_registry`);
  1. custom BRICK/REF/ns_ifc, `ns_inst` already ending in '/', and a
     registry of str values as the Qt widgets give them (QLineEdit.text()
     always yields str): empty `ifc_type`, empty `bacnet_name` (guard False
     although bacnet_type and bacnet_instance are present), `bacnet_name`
     present with empty `bacnet_instance`, and a bacnet_type needing both
     munging rules;
  2. an empty `QSettings` (the two region defaults for `ns_inst` and
     `ns_ifc`) and an empty registry (nothing but the bindings);
  3. error paths, one per call because the harness compares the two raises
     AND what each side wrote before raising: a row without `eq_guid`,
     without `point_id` (the original has already written the equipment's
     rdf:type triple, which the graph comparison exposes), without
     `point_type`, and an `ifc_type` of None.
"""
from rdflib import Graph, Namespace

from rdfeval.harness import run_pair, graphs_isomorphic

_MISSING = object()


def _bindings_ok(original, translated):
    """Every (prefix, namespace) the original graph binds, the translation binds too."""
    got = {(p, str(n)) for p, n in translated.namespaces()}
    return all((p, str(n)) in got for p, n in original.namespaces())


def _eq(a, b):
    if isinstance(a, Graph) and isinstance(b, Graph):
        return graphs_isomorphic(a, b) and _bindings_ok(a, b)
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

    def __init__(self, settings=None, brick=None, ref=None, registry=None):
        self.settings = _Settings(settings if settings is not None else {
            # deliberately WITHOUT a trailing '#'/'/', so the region's own
            # `if not str(base_inst).endswith(('#', '/')): base_inst += '#'`
            # is exercised identically on both sides.
            "ns_inst": "http://example.org/testproj",
        })
        self.BRICK = Namespace(brick or "https://brickschema.org/schema/Brick#")
        self.REF = Namespace(ref or "https://brickschema.org/schema/Brick/ref#")
        self.annotations_registry = (_annotations_registry()
                                     if registry is None else registry)

    def __eq__(self, other):
        if not isinstance(other, _FakeSelf):
            return NotImplemented
        keys = set(vars(self)) | set(vars(other))
        return all(_eq(getattr(self, k, _MISSING), getattr(other, k, _MISSING))
                   for k in keys)


def _custom():
    """BRICK, REF, ns_ifc and ns_inst that differ from every default (call 1)."""
    return _FakeSelf(
        settings={"ns_inst": "http://example.org/p/",
                  "ns_ifc": "http://example.org/ifc-custom#"},
        brick="http://example.org/brick-custom#",
        ref="http://example.org/ref-custom#",
        registry={
            "a": {  # every field a str, empty ifc_type -> IfcSensor default
                "eq_guid": "G1", "ifc_type": "",
                "point_id": "P1", "point_type": "Sensor",
                "bacnet_name": "T1", "bacnet_type": "AnalogInput",
                "bacnet_instance": "3",
            },
            "b": {  # empty name: guard False although the other fields exist
                "eq_guid": "G2", "ifc_type": "IfcActuator",
                "point_id": "P2", "point_type": "Command",
                "bacnet_name": "", "bacnet_type": "AnalogValue",
                "bacnet_instance": "4",
            },
            "c": {  # name present, empty instance, no type: ",".join of ""
                "eq_guid": "G3",
                "point_id": "P3", "point_type": "Setpoint",
                "bacnet_name": "N3", "bacnet_instance": "",
            },
            "d": {  # both munging rules are no-ops, upper case lowered
                "eq_guid": "G4", "ifc_type": "IfcSensor",
                "point_id": "P4", "point_type": "Sensor",
                "bacnet_name": "N4", "bacnet_type": "BinaryInput",
                "bacnet_instance": "0",
            },
        })


def _one_row(**fields):
    row = {"eq_guid": "E1", "point_id": "P1", "point_type": "Sensor"}
    row.update(fields)
    for k in [k for k, v in fields.items() if v is _MISSING]:
        del row[k]
    return {"r1": {"eq_guid": "E0", "point_id": "P0", "point_type": "Sensor"},
            "r2": row}


VERDICT = run_pair(
    __file__,
    entry="rebuild_output_graph",
    calls=[
        lambda: ((_FakeSelf(),), {}),
        lambda: ((_custom(),), {}),
        # region defaults for ns_inst and ns_ifc
        lambda: ((_FakeSelf(settings={}, registry=_one_row(
            ifc_type="IfcDoor", bacnet_name="N", bacnet_type="X",
            bacnet_instance="1")),), {}),
        # empty registry: only the bindings remain to compare
        lambda: ((_FakeSelf(settings={}, registry={}),), {}),
        # error paths (a first row is written before the second raises)
        lambda: ((_FakeSelf(registry=_one_row(eq_guid=_MISSING)),), {}),
        lambda: ((_FakeSelf(registry=_one_row(point_id=_MISSING)),), {}),
        lambda: ((_FakeSelf(registry=_one_row(point_type=_MISSING)),), {}),
        lambda: ((_FakeSelf(registry=_one_row(ifc_type=None)),), {}),
    ],
)

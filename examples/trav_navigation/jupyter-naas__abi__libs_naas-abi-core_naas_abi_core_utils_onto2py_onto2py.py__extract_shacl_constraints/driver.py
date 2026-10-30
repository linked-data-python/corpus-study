"""Validation driver for
jupyter-naas__abi__libs_naas-abi-core_naas_abi_core_utils_onto2py_onto2py.py__extract_shacl_constraints.

This region READS a graph, so the oracle is not isomorphism but the equality
of the values both versions produce from the same input graph (design record
corpus/405).  `fixture.ttl` is parsed fresh for each side.

`extract_shacl_constraints` returns nothing: its only observable effect is
the in-place mutation of `properties` (via the shimmed `process_property_shape`,
see context_shim.py).  `run_pair` compares every positional argument after
the call, not just the return value, so that mutation is exactly what gets
checked -- `classes` and `properties` are rebuilt fresh per call so mutation
from one side cannot leak into the other's input.

`SHACL` is a runtime parameter in the original code (not a fixed import), so
this driver supplies the real SHACL namespace explicitly; the translation
mirrors that by writing `{SHACL.NodeShape}` etc. as interpolated predicate
terms in the `m{ }` pattern instead of a `@prefix`.

`ordered=True`: several property shapes across different node shapes target
the SAME property path (ex:name: MaxOne, MaxFive, MaxNine in ex:ConflictShape,
MaxTwo in ex:OtherConflictShape, with five different sh:maxCount values),
and process_property_shape's writes to that shared PropertyInfo are
last-write-wins, so the order in which the join yields its triples decides
the final `properties` -- the only thing the driver can observe, since the
shim records nothing else. Then `ordered=True` bites: a mutant that iterates
the join in reverse ends with another maxCount for ex:name and fails. A
reordering that happens to end on the same last write (ex:MaxTwo) is not
seen: only the last write to a path is observable. The order is reachable in the
repository: extract_shacl_constraints (onto2py.py:1360) is run on the whole
ontology graph, where two node shapes may constrain one path with different
cardinalities. The sh:maxCount-less ex:NameShape / ex:AgeShape of the first
shape still exercise the fan-out (2 target classes x 2 property shapes), the
Python filter on `classes`, the zero-solution shape and the one-motif-only
neighbours.
"""
from pathlib import Path

from rdflib import Namespace

from rdfeval.harness import run_pair, fixture_graph
from context_shim import ClassInfo, PropertyInfo

FIXTURE = Path(__file__).parent / "fixture.ttl"

# The real SHACL vocabulary -- what the enclosing script actually passes as
# the `SHACL` parameter (see libs/naas-abi-core/naas_abi_core/utils/onto2py/onto2py.py:1286).
SH = Namespace("http://www.w3.org/ns/shacl#")


def _classes():
    return {
        "http://example.org/Person": ClassInfo(
            name="Person", uri="http://example.org/Person",
            parent_classes=[], properties=[],
        ),
        "http://example.org/Organisation": ClassInfo(
            name="Organisation", uri="http://example.org/Organisation",
            parent_classes=[], properties=[],
        ),
    }


def _properties():
    return {
        "http://example.org/name": PropertyInfo(
            name="name", property_type="data",
            range_classes={"str": None},
        ),
        "http://example.org/age": PropertyInfo(
            name="age", property_type="data",
            range_classes={"int": None},
        ),
    }


def _call():
    g = fixture_graph(FIXTURE)
    return (g, _classes(), _properties(), SH), {}


VERDICT = run_pair(
    __file__,
    entry='extract_shacl_constraints',
    calls=[_call],
    fixture="fixture.ttl",
    ordered=True,
)

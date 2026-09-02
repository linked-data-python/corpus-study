"""Validation driver for
RDFLib__pySHACL__pyshacl_constraints_core_string_based_constraints.py__MaxLengthConstraintComponent___init__.

``__init__(self, shape)`` either raises (bad/missing/multiple sh:maxLength
values) or mutates ``self`` in place and returns ``None``.

``run_pair``'s generic ``entry=``/``calls=`` path aborts the WHOLE driver
with an error verdict the moment either side raises (see harness.py: any
exception from ``fo``/``ft`` is caught around the pair of calls and reported
as ``verdict["error"]``, never compared) -- so it can only be used for the
one fixture that succeeds on both sides. The four fixtures that are meant to
raise ``ConstraintLoadError`` are exercised separately below, by calling each
side directly and comparing exception TYPE and message, then folded into the
same verdict/diff format so ``rdfeval check`` sees one outcome.

Cases covered, mirroring the region's three raising branches plus the
success path:
  * exactly one sh:maxLength, a plain positive xsd:integer -- success path,
    compared via run_pair (self.string_rules ends up holding it);
  * zero sh:maxLength values -- "at least one" ConstraintLoadError;
  * two sh:maxLength values -- "at most one" ConstraintLoadError;
  * one sh:maxLength that is not an integer-typed literal (xsd:string) --
    "must be a literal value with an integer" ConstraintLoadError;
  * one sh:maxLength that is a negative xsd:integer -- "must be a positive
    integer" ConstraintLoadError;
  * neighbourhood that must NOT match, folded into the zero-values fixture:
    an unrelated predicate on the shape node, and a sh:maxLength on a
    DIFFERENT node -- must not be picked up.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

from rdflib import Graph, Namespace

from pyshacl_shape_context import MaxLengthConstraintComponent, Shape
from rdfeval.harness import _exec_ldpy, _exec_python, run_pair

EX = Namespace("http://example.org/")

PREFIXES = """
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix ex: <http://example.org/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
"""

ONE_VALID = PREFIXES + """
ex:myShape sh:maxLength 10 .
"""

ZERO_VALUES = PREFIXES + """
ex:myShape ex:unrelated "noise" .
ex:otherShape sh:maxLength 5 .
"""

TWO_VALUES = PREFIXES + """
ex:myShape sh:maxLength 10, 20 .
"""

WRONG_TYPE = PREFIXES + """
ex:myShape sh:maxLength "ten"^^xsd:string .
"""

NEGATIVE = PREFIXES + """
ex:myShape sh:maxLength "-5"^^xsd:negativeInteger .
"""


def _shape(data: str, node=EX.myShape):
    g = Graph().parse(data=data, format="turtle")
    return Shape(g, node)


def _fixture(data: str):
    return lambda: ((MaxLengthConstraintComponent.__new__(MaxLengthConstraintComponent),
                     _shape(data)), {})


# run_pair() prints its own RDFEVAL-VERDICT line as a side effect;
# rdfeval.check takes the FIRST such line, so it has to be silenced here and
# re-emitted once, after the raising fixtures below have had a chance to
# turn a false "equivalent" into a real failure.
_buf = io.StringIO()
with contextlib.redirect_stderr(_buf):
    VERDICT = run_pair(
        __file__,
        entry="__init__",
        calls=[_fixture(ONE_VALID)],
    )

# The four raising fixtures: call each side's __init__ directly and compare
# the exception, since run_pair's generic path cannot.
if VERDICT["equivalent"]:
    here = Path(__file__).resolve().parent
    ns_o, _ = _exec_python(here / "original.py")
    ns_t, _ = _exec_ldpy(here / "translated.ldpy")
    fo, ft = ns_o["__init__"], ns_t["__init__"]

    diffs = []
    for name, data in [
        ("zero-values", ZERO_VALUES),
        ("two-values", TWO_VALUES),
        ("wrong-type", WRONG_TYPE),
        ("negative", NEGATIVE),
    ]:
        self_o = MaxLengthConstraintComponent.__new__(MaxLengthConstraintComponent)
        self_t = MaxLengthConstraintComponent.__new__(MaxLengthConstraintComponent)
        exc_o = exc_t = None
        try:
            fo(self_o, _shape(data))
        except Exception as e:  # noqa: BLE001 - comparing exception shape
            exc_o = e
        try:
            ft(self_t, _shape(data))
        except Exception as e:  # noqa: BLE001
            exc_t = e
        if (exc_o is None) != (exc_t is None):
            diffs.append(f"{name}: raised {exc_o!r} vs {exc_t!r}")
        elif exc_o is not None:
            if type(exc_o).__name__ != type(exc_t).__name__ or str(exc_o) != str(exc_t):
                diffs.append(f"{name}: {type(exc_o).__name__}({exc_o}) vs "
                             f"{type(exc_t).__name__}({exc_t})")
        else:
            diffs.append(f"{name}: expected both sides to raise, neither did")

    if diffs:
        VERDICT["equivalent"] = False
        VERDICT["diffs"] = VERDICT.get("diffs", []) + diffs

print("RDFEVAL-VERDICT " + json.dumps(VERDICT), file=sys.stderr)

"""Validation driver for kumagallium__asterism__ingest_tests_test_samples_curves.py__test_curves_aggregates.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a pytest test that takes two fixtures (`curves_csv`,
`tmp_path`); we reproduce them here as plain values so the entry point can
be called directly. `curves_csv` is the fixture body from
ingest/tests/test_samples_curves.py (same commit), verbatim: it writes the
same two-row CSV to a temp directory. `tmp_path` becomes a fresh
`tempfile.mkdtemp()` per call/side (the harness calls the fixture factory
once per side so no state leaks between them).

The calls after the first were added by the mutation audit (2026-10-31).
With the repository's two-row CSV alone, these translation mutants stayed
green: each `m{ {c79} {SD.x} ?o }` with its subject widened to `[]` (no
other curve carries aggregates), each one cut to its first solution
(`[:1]`, `.first()`: c79 has one value per aggregate), and each value
`assert` forced to `True` (the test passes). Each variant CSV is the
repository's, rewritten in one place, so that exactly one assertion decides:
  - "neighbour": a third curve with its own aggregates, the test still
    passes on the original; a widened subject sees two values;
  - "dup_<aggregate>": a third row that mints the SAME curve IRI
    (SID 6 / figure 79 / sample 113) and changes only that aggregate, so c79
    carries two values for it: the original fails on that assertion alone,
    a mutant that keeps one value, or skips that assertion, passes (the
    extra value is chosen so that the right one comes FIRST in store order:
    otherwise a truncating mutant would keep the wrong one, fail on the
    same assertion, and stay green);
  - "absent": the curve is not minted at all (SID changed): zero solutions
    for every read, the original fails on its first assertion.
The two datatype assertions are not exercised by any variant: the real
ingester always types the aggregates xsd:double / xsd:integer
(asterism/starrydata.py:435-442), so forcing them to True is an equivalent
mutant on every input the repository can produce.
"""
import csv
import tempfile
from pathlib import Path

from rdfeval.harness import run_pair


def _curves_csv(tmp_path: Path) -> Path:
    rows = [
        {
            "SID": "6",
            "DOI": "10.1021/am405410e",
            "composition": '"Pb1.00025Zn0.02Te1.02I0.0005"',
            "sample_id": "113",
            "figure_id": "79",
            "figure_name": '"6(b)"',
            "prop_x": '"Temperature"',
            "prop_y": '"Seebeck coefficient"',
            "unit_x": '"K"',
            "unit_y": '"V*K^(-1)"',
            "x": "[300, 400, 500, 600, 650]",
            "y": "[-0.0001, -0.0002, -0.0003, -0.0004, -0.00035]",
            "created_at": "",
            "updated_at": "",
            "project_names": '["ThermoelectricMaterials"]',
            "comments": '"figure (b)"',
        },
        {
            # Empty x/y to verify graceful handling
            "SID": "7",
            "DOI": "",
            "composition": '"Bi2Te3"',
            "sample_id": "114",
            "figure_id": "80",
            "figure_name": '"7"',
            "prop_x": '"Temperature"',
            "prop_y": '"Resistivity"',
            "unit_x": '"K"',
            "unit_y": '"ohm*cm"',
            "x": "",
            "y": "",
            "created_at": "",
            "updated_at": "",
            "project_names": "[]",
            "comments": "",
        },
    ]
    p = tmp_path / "curves.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    return p


# A single tmp_path/curves_csv pair, shared by BOTH sides: run_pair compares
# the call arguments too, so two independently-generated temp directories
# would differ trivially. ingest_curves() writes curves.ttl into the SAME
# tmp_path on both invocations (deterministic given the same curves_csv),
# so nothing leaks meaningfully between the two runs.
_tmp_path = Path(tempfile.mkdtemp())
_curves_csv_path = _curves_csv(_tmp_path)


def _fixture():
    return (_curves_csv_path, _tmp_path), {}


def _variant(edit):
    """A fresh tmp_path holding the repository's CSV after `edit(rows)`.

    Built once at import time and shared by both sides, like _tmp_path.
    """
    with _curves_csv_path.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    edit(rows)
    tmp = Path(tempfile.mkdtemp())
    p = tmp / "curves.csv"
    with p.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    args = (p, tmp)
    return lambda: (args, {})


def _extra(**changes):
    """Append a copy of the c79 row (rows[0]) with `changes` applied."""
    def edit(rows):
        rows.append({**rows[0], **changes})
    return edit


def _absent(rows):
    rows[0]["SID"] = "9"


_NOMINAL_Y = "[-0.0001, -0.0002, -0.0003, -0.0004, -0.00035]"
_VARIANTS = [
    _variant(_extra(SID="8", figure_id="81", sample_id="115",
                    x="[1, 2]", y="[5, 6]")),                           # neighbour
    _variant(_extra(x="[301, 400, 500, 600, 650]")),                    # dup_xMin
    _variant(_extra(x="[300, 400, 500, 600, 651]")),                    # dup_xMax
    _variant(_extra(y="[-0.0001, -0.0002, -0.0003, -0.00039, -0.00035]")),  # dup_yMin
    _variant(_extra(y="[-0.00005, -0.0002, -0.0003, -0.0004, -0.00035]")),  # dup_yMax
    _variant(_extra(x="[300, 400, 500, 600, 650, 400]",
                    y=_NOMINAL_Y[:-1] + ", -0.0002]")),                 # dup_pointCount
    _variant(_absent),                                                  # absent
]


VERDICT = run_pair(
    __file__,
    entry='test_curves_aggregates',
    calls=[_fixture, *_VARIANTS],
)

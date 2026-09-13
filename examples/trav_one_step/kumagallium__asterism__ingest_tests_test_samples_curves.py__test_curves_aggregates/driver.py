"""Validation driver for kumagallium__asterism__ingest_tests_test_samples_curves.py__test_curves_aggregates.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a pytest test that takes two fixtures (`curves_csv`,
`tmp_path`); we reproduce them here as plain values so the entry point can
be called directly. `curves_csv` is the fixture body from
ingest/tests/test_samples_curves.py (same commit), verbatim: it writes the
same two-row CSV to a temp directory. `tmp_path` becomes a fresh
`tempfile.mkdtemp()` per call/side (the harness calls the fixture factory
once per side so no state leaks between them).
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


VERDICT = run_pair(
    __file__,
    entry='test_curves_aggregates',
    calls=[_fixture],
)

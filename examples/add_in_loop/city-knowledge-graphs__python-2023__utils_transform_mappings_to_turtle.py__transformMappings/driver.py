"""Validation driver for city-knowledge-graphs__python-2023__utils_transform_mappings_to_turtle.py__transformMappings.

Establishes semantic equivalence of original.py and translated.ldpy.
Filled in during translation review; see rdfeval.harness for helpers.
"""
import shutil
import tempfile
from pathlib import Path

from rdfeval.harness import run_pair

_FIXTURE = Path(__file__).resolve().parent / "mappings_fixture.txt"


def _case():
    # transformMappings(filename) reads filename and writes filename's
    # ".ttl" sibling; give it a fresh temp copy per call (per side) so the
    # two runs never share a directory or an output file.
    tmpdir = Path(tempfile.mkdtemp(prefix="add_in_loop_"))
    dest = tmpdir / "mappings.txt"
    shutil.copyfile(_FIXTURE, dest)
    return (str(dest),), {}


# entry=None executes both modules and compares every rdflib Graph found in
# the module globals (plus captured stdout).  For function regions, set
# entry="<function name>" and provide the fixture arguments.
# The function returns None and only mutates its own local graph and a file
# on disk: the observable surface run_pair can compare is what it prints
# (g.serialize(format="turtle") to stdout) -- the fixture covers a CLS row,
# an OPROP row, a DPROP row (both collapse to owl:equivalentProperty) and an
# unrecognised "SKIP" row that must add nothing.
VERDICT = run_pair(
    __file__,
    entry='transformMappings',
    calls=[_case],
)

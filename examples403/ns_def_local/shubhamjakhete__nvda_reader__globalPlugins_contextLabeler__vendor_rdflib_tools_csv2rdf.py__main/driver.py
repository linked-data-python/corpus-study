"""Validation driver for
shubhamjakhete__nvda_reader__globalPlugins_contextLabeler__vendor_rdflib_tools_csv2rdf.py__main.

`main` (see original.py / meta.json) reads `sys.argv` directly and never
returns or builds an in-memory rdflib.Graph -- it writes n3-serialised
triples straight to `self.OUT` (a CSV2RDF instance attribute, `-o`
override). Both files carry an identical `demo(csv_path, out_path)` harness
that sets a minimal argv, calls `main`, and returns the text `main` wrote to
`out_path` -- that text is the region's only RDF-observable effect, so
meta.oracle: isomorphism is established here by comparing it as a string
(ordered=True, the default: row order is a simple sequential CSV scan on
both sides, not store-dependent).

`fixture.csv` is the CSV input `main` reads through `csv_reader` /
`fileinput.input` (two data rows so a translation that dropped a row would
be caught; a header row consumed as property names).  Both sides are called
with the *same* out_path (a fixed name in the system temp dir, computed once
below) rather than one fresh name per call: run_pair compares the `calls`
arguments themselves for equality, so two different randomly-generated names
would show up as a spurious diff.  This is safe because the two calls are
sequential, not concurrent (run_pair runs the original entirely -- write,
read back, return -- before it starts the translated one): each demo() call
overwrites and then immediately reads back the same path before the next
call touches it.
"""
import os
import tempfile
from pathlib import Path

from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent

_OUT_PATH = str(Path(tempfile.gettempdir()) / f"csv2rdf_demo_{os.getpid()}.n3")


def case():
    def make():
        return ((str(HERE / "fixture.csv"), _OUT_PATH), {})
    return make


VERDICT = run_pair(__file__, entry="demo", calls=[case()])

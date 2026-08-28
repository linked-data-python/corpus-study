"""Validation driver for pySHACL's assets/make_builtin.py.

Module-level region: it parses four Turtle assets from the *current directory*
into named graphs and pickles the resulting stores.  The harness compares every
rdflib Graph left in the module globals (here `g`, the last one built) plus
stdout.

Because the region reads "./schema.ttl" & co. and writes "./*.pickle" next to
them, the driver runs both representations in a scratch directory into which
the four .ttl assets are copied from the corpus checkout
(RDFLib/pySHACL@469cca7a22, Apache-2.0).  They total ~1.4 MB, too large to
vendor in the example directory, and the corpus copy is never written to.
The scratch directory (and the ~4.6 MB of pickles the region writes) is removed
afterwards.

Context shim: pyshacl/ next to this driver is a stub package exposing a
verbatim copy of pyshacl/monkey/__init__.py, so that
`from pyshacl.monkey import apply_patches` resolves without pySHACL being
installed.  Both representations import it identically (same process).
"""
import os
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

ASSETS = HERE.parents[2] / "corpus" / "repos" / "RDFLib__pySHACL" / "pyshacl" / "assets"
TTL = ("schema.ttl", "shacl.ttl", "dash.ttl", "shacl-shacl.ttl")

from rdfeval.harness import run_pair

workdir = Path(tempfile.mkdtemp(prefix="make_builtin-"))
cwd = Path.cwd()
try:
    for name in TTL:
        shutil.copy(ASSETS / name, workdir / name)
    os.chdir(workdir)
    VERDICT = run_pair(__file__, entry=None, calls=None)
finally:
    os.chdir(cwd)
    shutil.rmtree(workdir, ignore_errors=True)

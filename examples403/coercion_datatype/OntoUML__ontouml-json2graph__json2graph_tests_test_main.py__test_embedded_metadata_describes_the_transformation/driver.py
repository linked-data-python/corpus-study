"""Validation driver for OntoUML__ontouml-json2graph__json2graph_tests_test_main.py__test_embedded_metadata_describes_the_transformation.

EXCLUDED (see meta.json). The region is an end-to-end pytest test whose body
shells out to the project's own CLI --
`run_metadata_cli` (a sibling helper, not carried by the extraction) runs
`subprocess.run([sys.executable, "-m", "json2graph.decode", ...])` -- to
produce the very `cardinality.ttl` file it then parses and asserts against,
and also calls three more sibling helpers not carried either
(write_cardinality_project, get_output_artifact, get_recorded_configuration;
all defined elsewhere in the ~1800-line json2graph/tests/test_main.py).
Reproducing them in a context shim would mean re-implementing the OntoUML
json2graph CLI itself -- the system under test, not context around it, which
is exactly what a shim must not do (AGENT_BATCH.md: "N'inventez pas de
logique"). context.py (see meta.json) fixes the one dependency that *was*
just a broken relative import (content_identity/metadata), so the failure
`rdfeval check` records below is the real, irreducible one: a NameError on
the first genuinely-missing helper, not an import-path artefact.

The fixture is still the real signature (a writable tmp_path), so both sides
fail identically and at the same line.
"""
import tempfile
from pathlib import Path

from rdfeval.harness import run_pair


def _fixture():
    return ((Path(tempfile.mkdtemp()),), {})


VERDICT = run_pair(
    __file__,
    entry='test_embedded_metadata_describes_the_transformation',
    calls=[_fixture],
)

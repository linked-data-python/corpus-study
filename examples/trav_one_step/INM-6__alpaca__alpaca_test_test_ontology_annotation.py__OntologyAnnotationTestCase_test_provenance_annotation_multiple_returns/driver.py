"""Validation driver for INM-6__alpaca__alpaca_test_test_ontology_annotation.py__OntologyAnnotationTestCase_test_provenance_annotation_multiple_returns.

EXCLUDED (see meta.json). Both original.py and translated.ldpy do
`from alpaca import activate, deactivate, Provenance, save_provenance` at
module level, and `alpaca` (alpaca-prov on PyPI, the real provenance-capture
library this test is about) is not installed in this study's venv (verified:
`~/.venvs/ldpy/bin/python -c "import alpaca"` -> ModuleNotFoundError).
`_exec_python`/`_exec_ldpy` therefore fail identically at the very top of
the region, on *both* sides, before `entry`/`calls` is ever reached.

The region's real body also calls `InputObject()` and `process_multiple(...)`
-- a class and an `@alpaca.Provenance`-decorated function defined earlier in
the same ~1000-line test file, not carried by the extraction -- and reads
`self.ONTOLOGY`, set by the test case's own `setUpClass`. None of this is a
context-shim job: a shim restores a broken *binding* (an import path, a
constant); `InputObject`/`process_multiple` only mean anything together with
`alpaca.Provenance`'s real call-stack introspection, which actually builds
the PROV graph this test then reads. Reproducing that would mean
re-implementing the system under test, which AGENT_BATCH.md forbids
("n'inventez pas de logique") -- and it would be moot regardless, since the
`from alpaca import ...` line fails before either binding is ever needed.

alpaca's own requirements.txt (numpy, networkx, dill, joblib, rdflib, tqdm)
is lighter than the repository's examples/docs extras (matplotlib, nixio,
neo, elephant, quantities) might suggest, but installing it and its
dependencies into this study's shared, version-pinned venv (rdflib==7.2.1,
for reproducibility across the whole corpus study) is out of scope for a
single region's translation and was not done.

The rdflib read sites themselves WERE translated in full (see translated.ldpy
and translation_notes in meta.json) and checked independently: the file
transpiles cleanly on its own --

    ~/.venvs/ldpy/bin/python -c "from ldpy.transpiler import transpile; \
        transpile(open('translated.ldpy').read(), filename='translated.ldpy')"

-- which only requires the island syntax to be valid, not `alpaca` to be
importable. No `calls=` fixture can make this reach any of those sites: the
import fails first, for both sides, so any fixture list would be theatre.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_provenance_annotation_multiple_returns',
    calls=[((), {})],  # never reached: the ModuleNotFoundError above fires
                        # while loading original.py/translated.ldpy, before
                        # entry is looked up
)

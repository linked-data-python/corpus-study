"""Validation driver for
CatholicOS__ontokit-api__tests_unit_test_linter.py__test_missing_language_tag_plain_literal.

EXCLUDED (see meta.json). Both original.py and translated.ldpy
`from ontokit.services.linter import (...)` at module level: `ontokit`
(CatholicOS/ontokit-api) is the source repository's OWN package -- the
system under test in this test file, not a general-purpose third-party
library. It is not installed in the shared `~/.venvs/ldpy` interpreter
(confirmed: `import ontokit` -> ModuleNotFoundError), and unlike the wntr
precedent for this same "excluded" outcome, it is not on PyPI either
(`pip index versions ontokit-api` / `ontokit` both come back "No matching
distribution found"): there is no install step that would fix this region,
only vendoring or reimplementing the CatholicOS/ontokit-api project's
`OntologyLinter` -- which is exactly what a shim must never do (a shim
restores a broken *binding*, never reimplements the system under test; see
the vitalgraph precedent this file's exclusion follows).

The region's own `add_run_shared_subject` triples ARE fully expressible
and were translated: the two `g.add((EX.Animal, ...))` calls on the shared
subject `ex:Animal` fold into one `+{ ex:Animal a owl:Class ; rdfs:label
"Animal" }` under `@graph g`. What blocks execution is entirely downstream
of that -- the call to `OntologyLinter(...).lint(g, PROJECT_ID)` and the
test helper `_results_with_rule`, both belonging to the untranslated,
unavailable `ontokit` package.

_exec_python/_exec_ldpy fail identically at the `from ontokit...` import,
on *both* sides, before `entry`/`calls` is ever reached -- so the fixture
list below is theatre, kept only so the driver is ready to run for real if
`ontokit` ever becomes installable in this venv.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_missing_language_tag_plain_literal',
    calls=[((), {})],  # never reached: ModuleNotFoundError fires while
                        # loading original.py/translated.ldpy
)

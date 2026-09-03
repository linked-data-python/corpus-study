"""Validation driver for FAIRDataTeam__fdpneo-server__tests_unit_metadata_test_extensions.py__test_page_honours_limit_and_offset.

EXCLUDED (see meta.json): this region does not read an externally-supplied
graph at all.  The graph it parses (``g.parse(data=response.text, ...)``) is
the Turtle body of an HTTP response returned by a FastAPI app built in the
test itself (``_build_app``/``_repo_with_catalogs``/``_FakePDP``/
``_two_level_cache``), none of which are in the extracted context (they sit
elsewhere in the same test file) and none of which this venv can run: the
test needs ``fastapi`` (not installed here) plus the production
``fdpneo_server`` package's identity/metadata/policy/shared modules, which
implement the very pagination logic the trav_one_step read is exercising --
reconstructing them would mean re-implementing production application code,
not restoring a binding, so no context shim is provided.

The single positional-fixture-argument wiring (``fixture=`` -> one Graph
passed to ``entry``) does not fit either: the entry point takes no arguments
at all, so it is called with none.  Left in place mainly so ``rdfeval check``
reports the real blocker (a missing ``fastapi``/``fdpneo_server`` import,
raised while executing ``original.py`` itself) rather than a misleading
argument-count error.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_page_honours_limit_and_offset',
    calls=[((), {})],
    # ordered=True only if the region imposes an order (sorted, ORDER BY):
    # no store promises one, so results are compared as multisets.
)

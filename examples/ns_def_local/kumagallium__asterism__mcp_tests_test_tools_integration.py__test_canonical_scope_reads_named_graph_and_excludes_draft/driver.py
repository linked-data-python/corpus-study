"""Validation driver for kumagallium__asterism__mcp_tests_test_tools_integration.py__test_canonical_scope_reads_named_graph_and_excludes_draft.

excluded (see meta.json): the region depends on the real
`asterism_mcp.tools.sample_search` and `asterism.substrate` helpers, neither
installed in this study's venv nor included in the extraction. Reconstructing
them would mean reimplementing the canonical/draft graph selection that is
the very thing the test exercises, not restoring a binding.

The 0-argument async entry is called directly (no fixture=-driven wiring,
which does not fit this signature) so that `rdfeval check` surfaces the real
blocker: both `original.py` and `translated.ldpy` already fail at
`from asterism.substrate import (...)` (ModuleNotFoundError), before the
canonical/draft graphs are ever built.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='test_canonical_scope_reads_named_graph_and_excludes_draft',
    calls=[lambda: ((), {})],
)

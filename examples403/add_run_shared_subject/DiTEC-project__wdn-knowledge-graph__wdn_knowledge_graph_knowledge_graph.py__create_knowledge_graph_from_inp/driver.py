"""Validation driver for DiTEC-project__wdn-knowledge-graph__wdn_knowledge_graph_knowledge_graph.py__create_knowledge_graph_from_inp.

EXCLUDED (see meta.json). Both original.py and translated.ldpy `import wntr`
at module level -- wntr (Water Network Tool for Resilience) is a real,
pip-installable package (confirmed reachable: `pip index versions wntr`
lists 1.5.0/1.4.0/1.3.2/... on this network), pinned to 1.3.2 in the source
repository's requirements.txt, but it is NOT present in `~/.venvs/ldpy`, the
single shared interpreter this study standardises on across every region
and every concurrently running agent. Installing a heavy third-party
scientific package (C-extension build, EPANET binary) into that shared venv
is outside one region's scope -- it is not a context-shim job: a shim
restores a broken *binding* (an import path, a constant, a class copied
verbatim from the project), never a missing third-party dependency of the
interpreter itself, and doing so here would affect every other example and
every other agent using the same venv concurrently.

Unlike the vital-graph precedent for this same "excluded" outcome (whose
`vitalgraph` store is unpublished and would need reimplementing to run at
all), the corpus clone for this repository DOES carry a real, usable input
file at corpus/repos/DiTEC-project__wdn-knowledge-graph/sample_data/
LeakDB_Scenario-1.inp (~5.2 MB, not copied into this region directory: it
would dominate the pair's size for no comparison benefit while wntr itself
is absent). So this region is a strictly *installation* gap, not a
"cannot be executed without reimplementing the system under test" one: once
`wntr==1.3.2` is available in the shared venv, `create_knowledge_graph_from_inp`
can be called directly against that .inp file on both sides with no further
context restoration.

_exec_python/_exec_ldpy fail identically at the very first line of the
region (`import wntr`, ModuleNotFoundError), on *both* sides, before
`entry`/`calls` is ever reached -- so any fixture list below is theatre,
kept only so the driver is ready to run for real the moment wntr is
installed.
"""
from rdfeval.harness import run_pair

VERDICT = run_pair(
    __file__,
    entry='create_knowledge_graph_from_inp',
    calls=[
        ((), {"inp_file": "../../../corpus/repos/DiTEC-project__wdn-knowledge-graph/sample_data/LeakDB_Scenario-1.inp"}),
    ],  # never reached: the ModuleNotFoundError above fires while loading
        # original.py/translated.ldpy, before entry is looked up
)

"""Validation driver for semanticarts__ontology-toolkit__onto_tool_bundle.py____bundle_transform_sparql__.

__bundle_transform_sparql__ takes no graph argument: it reads an input file
named by `action['source']`, runs a SPARQL UPDATE over it (with prefixes
supplied via `initNs`) and writes the result to `action['target']`. None of
that is a return value or an in-place graph mutation the generic
run_pair(entry=...) machinery can see, so this driver calls the function
directly for each side, from a fresh temp output file, and compares what
each side wrote by isomorphism -- the reading oracle applied to the file it
produces rather than a value it returns (design record corpus/405).
"""
import sys
import tempfile
import traceback
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic

EX_DIR = Path(__file__).resolve().parent
FIXTURE = EX_DIR / "fixture.ttl"

# No PREFIX line for rdfs: here on purpose -- the region supplies it via
# initNs={'rdfs': RDFS, ...}, which is exactly the bind_initbindings site.
# Braces are doubled because the region itself runs tool['query'].format(...)
# on this text before parsing it as SPARQL.
UPDATE_QUERY = """
DELETE {{ ?s rdfs:label "old" }}
INSERT {{ ?s rdfs:label "new" }}
WHERE {{ ?s rdfs:label "old" }}
"""


def _run(execfn, filename):
    ns, _out = execfn(EX_DIR / filename)
    fn = ns.get("__bundle_transform_sparql__")
    with tempfile.TemporaryDirectory() as td:
        outfile = str(Path(td) / "out.ttl")
        action = {"source": str(FIXTURE), "target": outfile}
        tool = {"query": UPDATE_QUERY}
        fn(action, tool, {})
        return Graph().parse(outfile, format="turtle")


verdict = {"example": EX_DIR.name, "equivalent": False,
           "method": "custom:file-io", "diffs": [], "error": None}
try:
    g_original = _run(_exec_python, "original.py")
    g_translated = _run(_exec_ldpy, "translated.ldpy")
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)
    _emit(verdict)
    sys.exit(0)

diffs = []
if not graphs_isomorphic(g_original, g_translated):
    diffs.append(f"output graphs not isomorphic "
                 f"({len(g_original)} vs {len(g_translated)} triples)")
verdict["diffs"] = diffs
verdict["equivalent"] = not diffs
VERDICT = verdict
_emit(verdict)

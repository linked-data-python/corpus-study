"""Validation driver for Haoyu-R__SeLoC-ML__tflite2semantic_user_input.py__tflite2semantic.

Establishes semantic equivalence of original.py and translated.ldpy.

The region is a module-level for-loop, not a function: `g` is a
module-level Graph both sides build in place, so module-state comparison
(every rdflib Graph in the module globals) is the region's own oracle --
isomorphism, matching meta.json's "oracle": "isomorphism".  Two runs:

  as-written  -- run_pair on the two artefacts as they are (entry=None):
                 the graph `g`, by isomorphism, and the shared module values
                 (sensorOfNN, i, value ...).
  repo-graph  -- the same two artefacts, copied to a temporary directory
                 with `g = Graph()` replaced by what `g` really is in the
                 repository when the loop runs: the module graph of
                 tflite2semantic_user_input.py, lines 17-41, which binds
                 nine prefixes (`schema`, `sosa_extend`, `ssn_extend` among
                 them) and is serialised to Turtle at the end of the script
                 (lines 473 and 476).  Compared: `g` by isomorphism, and
                 every prefix binding the original's `g` carries must be on
                 the translation's (extra bindings are tolerated).  This is
                 what catches an `@graph g` whose `@prefix sdo:` rebinds
                 https://schema.org/ away from the repository's `schema:`.
"""
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

ex_dir = Path(__file__).resolve().parent

GRAPH_LINE = "g = Graph()\n"
# tflite2semantic_user_input.py@5ecc52c25e, lines 17-41, verbatim
# (ssn_extend and sosa_extend are already defined by both artefacts).
REPO_GRAPH = '''SOSA = Namespace("http://www.w3.org/ns/sosa/")
SSN = Namespace("http://www.w3.org/ns/ssn/")
nnet = Namespace("https://w3id.org/tinyml-schema/neural-network-schema#")
s3n = Namespace("http://w3id.org/s3n/")
ssn_system = Namespace("http://www.w3.org/ns/ssn/systems/")
s3n_extend = Namespace("https://w3id.org/tinyml-schema/neural-network-schema/s3n_extend/")
om = Namespace("http://www.ontology-of-units-of-measure.org/resource/om-2/")
from rdflib.namespace import SDO
g = Graph()
nm = g.namespace_manager
nm.bind("sosa", SOSA)
nm.bind("nnet", nnet)
nm.bind("schema", SDO)
nm.bind("s3n", s3n)
nm.bind("ssn", SSN)
nm.bind("om", om)
nm.bind("ssn_extend", ssn_extend)
nm.bind("sosa_extend", sosa_extend)
nm.bind("s3n_extend", s3n_extend)
'''


def _quiet(**kwargs) -> dict:
    """run_pair's verdict without its stderr line: this driver emits one."""
    with contextlib.redirect_stderr(io.StringIO()):
        return run_pair(**kwargs)


def _repo_graph() -> list[str]:
    left, right = harness.sides_from_env()
    work = Path(tempfile.mkdtemp(prefix="seloc_tflite2semantic_"))
    try:
        graphs = []
        for name, label in ((left, "__original__"), (right, "__translated__")):
            text = (ex_dir / name).read_text()
            if text.count(GRAPH_LINE) != 1:
                return [f"repo-graph: `g = Graph()` not found once in {name}"]
            (work / name).write_text(text.replace(GRAPH_LINE, REPO_GRAPH))
            ns, _ = harness._exec_artefact(work / name, label)
            graphs.append(ns["g"])
    finally:
        shutil.rmtree(work, ignore_errors=True)
    go, gt = graphs
    diffs = []
    if not harness.graphs_isomorphic(go, gt):
        diffs.append(f"repo-graph: graphs not isomorphic ({len(go)} vs {len(gt)} triples)")
    missing = set(go.namespaces()) - set(gt.namespaces())
    if missing:
        diffs.append("repo-graph: prefix bindings lost "
                     f"{sorted((p, str(n)) for p, n in missing)}")
    return diffs


as_written = _quiet(driver_file=__file__, entry=None, calls=None)
try:
    repo = _repo_graph()
    repo_error = None
except Exception:
    import traceback
    repo, repo_error = [], traceback.format_exc(limit=8)

verdict = dict(as_written)
verdict["method"] = f"{as_written.get('method')} (as-written + repo-graph bindings)"
verdict["diffs"] = [f"as-written: {d}" for d in as_written.get("diffs", [])] + repo
errors = [e for e in (as_written.get("error"), repo_error) if e]
verdict["error"] = "\n".join(errors) or None
verdict["equivalent"] = bool(as_written.get("equivalent")) and not repo and not repo_error
print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
VERDICT = verdict

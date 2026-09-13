"""Validation driver for temcdrm__emthub__src_emthub_examples_ic_to_rdf.py__create_cim_ic.

``create_cim_ic`` returns nothing and mutates only a graph local to the
function: its one observable effect is the Turtle file it serializes to
disk (``case['name'] + '_ic.ttl'``). That falls exactly into the gap
``rdfeval.harness.run_pair`` documents for entry/calls mode ("the entry
point returns None, takes no argument to mutate and prints nothing" -- a
file write is invisible to it). So this driver calls both sides directly
(reusing the harness's own exec/compare helpers) and instead compares the
*serialized graph* it reads back from each side's output file.

Input fixtures: three small CSV-like ``.txt`` files (bus/gen/branch initial
conditions), covering a line branch (tap == 0) and a transformer branch
(tap > 0) so both ``SvLinePF``/``SvXfmrPF`` naming paths run.
"""
import shutil
import sys
import tempfile
from pathlib import Path

from rdflib import Graph

from rdfeval.harness import _emit, _exec_ldpy, _exec_python, graphs_isomorphic

EX_DIR = Path(__file__).resolve().parent

BUS_TXT = """bus,basekv,vpu,angle,cnid
1,138.0,1.02,-3.5,http://example.org/CN1
2,138.0,0.98,-5.0,http://example.org/CN2
"""

BR_TXT = """from,to,tap,pf,qf,pt,qt,t1id,t2id
1,2,0.0,0.10,0.02,-0.10,-0.02,http://example.org/EQ1_T1,http://example.org/EQ1_T2
3,4,1.0,0.20,0.03,-0.20,-0.03,http://example.org/EQ2_T1,http://example.org/EQ2_T2
"""

GEN_TXT = """name,p,q,type,t1id
G1,0.5,0.10,PV,http://example.org/EQ3_T1
"""


def _make_case(tmpdir: Path) -> dict:
    prefix = tmpdir / "case"
    (tmpdir / "casemb.txt").write_text(BUS_TXT)
    (tmpdir / "casembr.txt").write_text(BR_TXT)
    (tmpdir / "casemg.txt").write_text(GEN_TXT)
    return {"name": str(prefix)}


def _run_side(exec_fn, path: Path, tmpdir: Path) -> Graph:
    ns, _out = exec_fn(path)
    case = _make_case(tmpdir)
    ns["create_cim_ic"](case)
    ttl_path = Path(case["name"] + "_ic.ttl")
    g = Graph().parse(source=str(ttl_path), format="turtle")
    return g


verdict: dict = {"example": EX_DIR.name, "equivalent": False,
                 "method": "output-file:create_cim_ic", "diffs": [], "error": None}
try:
    tmp_o = Path(tempfile.mkdtemp(prefix="rdfeval-orig-"))
    tmp_t = Path(tempfile.mkdtemp(prefix="rdfeval-trans-"))
    try:
        g_o = _run_side(_exec_python, EX_DIR / "original.py", tmp_o)
        g_t = _run_side(_exec_ldpy, EX_DIR / "translated.ldpy", tmp_t)
        if not graphs_isomorphic(g_o, g_t):
            verdict["diffs"].append(
                f"output graphs not isomorphic ({len(g_o)} vs {len(g_t)} triples)"
            )
    finally:
        shutil.rmtree(tmp_o, ignore_errors=True)
        shutil.rmtree(tmp_t, ignore_errors=True)
except Exception:
    import traceback
    verdict["error"] = traceback.format_exc(limit=8)
    _emit(verdict)
    sys.exit(0)

verdict["equivalent"] = not verdict["diffs"]
_emit(verdict)
VERDICT = verdict

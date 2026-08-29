"""Validation driver for
Display-Lab__scaffold__src_utils_namespace__PSDO.py__<module>_3.

The region is one line, `from src.utils.namespace import
AliasingDefinedNamespace` (rdf_ops: 0, kind: statement) -- no graph, no
function, nothing at module level but the import itself.  The generic
``run_pair(entry=None)`` oracle compares rdflib Graphs found in globals plus
captured stdout; here that is empty on both sides regardless of whether the
translation is right, so it always reports "nothing observable to compare".
See meta.json: no construction from INSTRUCTIONS_403 §4 applies to this
import (it is not `from project import BRICK, SH`, see below), so there is
nothing to add to either file to manufacture an island-based observable
without inventing content foreign to the one-line region -- forbidden by
AGENT_BATCH.

What IS a real, non-fabricated check, in the same spirit as the generic
oracle's own graph-by-variable-name comparison: does the name
`AliasingDefinedNamespace` resolve to an equivalent class on both sides?
Both original.py and translated.ldpy import it from the same context shim
(namespace_context.py, cached once in sys.modules), so it is in fact the
SAME object on both sides -- this driver checks that explicitly rather than
assuming it.
"""
import traceback
from pathlib import Path

from rdfeval.harness import _exec_ldpy, _exec_python, _emit


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:import-identity", "diffs": [],
                     "error": None}
    try:
        ns_o, out_o = _exec_python(ex_dir / "original.py")
        ns_t, out_t = _exec_ldpy(ex_dir / "translated.ldpy")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        _emit(verdict)
        return verdict

    diffs: list[str] = []
    if out_o != out_t:
        diffs.append("stdout differs")

    cls_o = ns_o.get("AliasingDefinedNamespace")
    cls_t = ns_t.get("AliasingDefinedNamespace")
    if cls_o is None or cls_t is None:
        diffs.append(f"AliasingDefinedNamespace not bound on both sides "
                     f"(original: {cls_o!r}, translated: {cls_t!r})")
    elif cls_o is not cls_t:
        diffs.append(f"AliasingDefinedNamespace: different objects bound "
                     f"({cls_o!r} vs {cls_t!r})")
    elif cls_o.__name__ != "AliasingDefinedNamespace":
        diffs.append(f"AliasingDefinedNamespace: unexpected class {cls_o!r}")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()

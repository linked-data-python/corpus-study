"""Validation driver for
mhrimaz__aasbrain-concept-description-repo__app_models_aas_namespace.py__<module>_1.

Not the generic ``run_pair(entry=None)`` shape: the region defines no
``rdflib.Graph`` and its only module-level value is a *class*
(``AASNameSpace``), which ``rdfeval.harness._values`` deliberately excludes
(a class has no meaningful ``__eq__``, so including it would report a
difference on every pair). What the region actually produces are the three
RDF terms held as class attributes (``AAS``, ``CD_TYPE``, ``ID``). Compare
those directly.
"""
import sys
import traceback
from pathlib import Path

from rdfeval.harness import _emit, _exec_ldpy, _exec_python

ATTRS = ["AAS", "CD_TYPE", "ID"]


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:class-attributes", "diffs": [],
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

    cls_o, cls_t = ns_o.get("AASNameSpace"), ns_t.get("AASNameSpace")
    if cls_o is None or cls_t is None:
        diffs.append("AASNameSpace class missing on one side")
    else:
        for attr in ATTRS:
            vo, vt = str(getattr(cls_o, attr)), str(getattr(cls_t, attr))
            if vo != vt:
                diffs.append(f"AASNameSpace.{attr}: {vo!r} vs {vt!r}")

    verdict["attrs_compared"] = ATTRS
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    _emit(verdict)
    return verdict


VERDICT = main()

if __name__ == "__main__":
    sys.exit(0 if VERDICT["equivalent"] else 1)

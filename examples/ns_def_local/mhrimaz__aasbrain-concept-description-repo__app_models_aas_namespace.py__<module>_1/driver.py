"""Validation driver for
mhrimaz__aasbrain-concept-description-repo__app_models_aas_namespace.py__<module>_1.

Not the generic ``run_pair(entry=None)`` shape: the region defines no
``rdflib.Graph`` and its only module-level value is a *class*
(``AASNameSpace``), which ``rdfeval.harness._values`` deliberately excludes
(a class has no meaningful ``__eq__``, so including it would report a
difference on every pair). What the region actually produces are the three
RDF terms held as class attributes (``AAS``, ``CD_TYPE``, ``ID``). Compare
those directly, on everything the rest of the repository relies on:

  * the string value of each attribute (``str``);
  * its TYPE.  String equality is blind to it: a ``CD_TYPE`` stored as a
    ``str`` or a ``Literal``, or an ``AAS`` stored as a plain string, passes
    a ``str`` comparison.  The repository needs a ``Namespace`` (it indexes
    ``AASNameSpace.AAS["…"]`` in some 300 places, e.g.
    app/models/administrative_information.py:42-57) and URIRef terms;
  * the class's own attribute names: the ``@prefix`` in the class body must
    not leave anything else there, nor drop anything;
  * what the repository does with ``AAS``: ``AAS["x"]`` and ``AAS.x``
    (value and type), and ``graph.bind("aas", AASNameSpace.AAS)``
    (app/models/key.py:49 and ten other models), whose bindings are compared.
"""
import sys
import traceback
from pathlib import Path

from rdflib import Graph

from rdfeval import harness

ATTRS = ["AAS", "CD_TYPE", "ID"]


def _own(cls):
    return sorted(k for k in vars(cls)
                  if not (k.startswith("__") and k.endswith("__")))


def _uses(cls):
    """What the repository does with AASNameSpace.AAS, as (value, type)."""
    aas = cls.AAS
    g = Graph(bind_namespaces="none")
    g.bind("aas", aas)
    return {
        'AAS["Identifiable/id"]': (str(aas["Identifiable/id"]),
                                   type(aas["Identifiable/id"]).__name__),
        "AAS.idShort": (str(aas.idShort), type(aas.idShort).__name__),
        'bind("aas", AAS)': sorted((p, str(n)) for p, n in g.namespaces()),
    }


def main() -> dict:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "custom:class-attributes (value, type, "
                               "own names, repository uses)",
                     "diffs": [], "error": None}
    try:
        left, right = harness.sides_from_env()
        ns_o, out_o = harness._exec_artefact(ex_dir / left, "__original__")
        ns_t, out_t = harness._exec_artefact(ex_dir / right, "__translated__")
        verdict["sides"] = [left, right]
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        harness._emit(verdict)
        return verdict

    diffs: list[str] = []
    if out_o != out_t:
        diffs.append("stdout differs")

    cls_o, cls_t = ns_o.get("AASNameSpace"), ns_t.get("AASNameSpace")
    if cls_o is None or cls_t is None:
        diffs.append("AASNameSpace class missing on one side")
    else:
        if _own(cls_o) != _own(cls_t):
            diffs.append(f"class attributes differ: {_own(cls_o)} vs {_own(cls_t)}")
        for attr in ATTRS:
            ao, at = getattr(cls_o, attr, None), getattr(cls_t, attr, None)
            if str(ao) != str(at):
                diffs.append(f"AASNameSpace.{attr}: {str(ao)!r} vs {str(at)!r}")
            if type(ao) is not type(at):
                diffs.append(f"AASNameSpace.{attr}: type {type(ao).__name__} "
                             f"vs {type(at).__name__}")
        try:
            uo, ut = _uses(cls_o), _uses(cls_t)
            for k in uo:
                if uo[k] != ut[k]:
                    diffs.append(f"{k}: {uo[k]!r} vs {ut[k]!r}")
        except Exception as e:                    # noqa: BLE001 - reported
            diffs.append(f"repository uses of AAS raise: {type(e).__name__}: {e}")

    verdict["attrs_compared"] = ATTRS
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    harness._emit(verdict)
    return verdict


VERDICT = main()

if __name__ == "__main__":
    sys.exit(0 if VERDICT["equivalent"] else 1)

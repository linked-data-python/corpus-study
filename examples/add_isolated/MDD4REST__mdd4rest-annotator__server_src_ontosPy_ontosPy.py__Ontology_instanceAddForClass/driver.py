"""Validation driver for MDD4REST__mdd4rest-annotator__server_src_ontosPy_ontosPy.py__Ontology_instanceAddForClass.

instanceAddForClass mutates ``self.sessionGraph`` (a context_shim.OntologyContext
attribute, see context_shim.py) rather than returning or receiving a graph as
an ordinary argument/return value. run_pair's built-in entry=/calls=
comparison calls the entry point once per side with a FRESH `self` per
run.docstring's own words) and then compares each positional argument
-- including that `self` -- with plain ``==``: OntologyContext defines no
``__eq__``, so two independently-built instances (identical attributes, but
never the SAME object) are never equal, regardless of translation. Comparing
the raw `self` argument would therefore report a difference on every run --
a false FAIL, not a signal about the region.

So, following the precedent of driving both sides by hand set by
add_isolated/BBDFrancois.../driver.py and add_isolated/TheWorldAvatar/.../
driver.py (a region whose real state does not travel through run_pair's
default comparison), this driver builds one OntologyContext per side per
case, calls instanceAddForClass, and compares:

  * the returned instance URIRef (or the raised exception's type + message,
    for the two error branches) -- via plain equality (rdflib terms compare
    by value);
  * the resulting ``sessionGraph`` -- by isomorphism, the add_isolated oracle
    (design record corpus/403).

Six cases exercise every branch:
  * A -- URIRef instance, class allowed: the `type(anInstance) == URIRef`
    branch, self.sessionGraph.add((anInstance, RDF.type, aClass)).
  * B -- string instance, class allowed, ns=None: falls back to
    self.sessionNS (the `ns = ns or self.sessionNS` line).
  * C -- string instance, class allowed, ns given explicitly: the passed
    `ns` wins over self.sessionNS.
  * D -- class NOT in self.allclasses: the outer `else` raises.
  * E -- class allowed, anInstance neither URIRef nor string (an int): the
    inner `else` raises.
  * F -- empty string instance (edge of the string branch, `ns[""]` -- the
    class's own IRI as the instance).
"""
from __future__ import annotations

import traceback
from pathlib import Path

from rdflib import Namespace, URIRef

from rdfeval.harness import _exec_ldpy, _exec_python, _emit, graphs_isomorphic

HERE = Path(__file__).resolve().parent

CLASS_A = URIRef("http://example.org/onto#ClassA")
CLASS_B = URIRef("http://example.org/onto#ClassB")
ALT_NS = Namespace("http://example.org/alt/")

CASES = [
    ("A instance is a URIRef",
     dict(allclasses=[CLASS_A, CLASS_B]), CLASS_A, URIRef("http://example.org/inst/1"), None),
    ("B instance is a string, default ns",
     dict(allclasses=[CLASS_A]), CLASS_A, "widget-1", None),
    ("C instance is a string, explicit ns",
     dict(allclasses=[CLASS_A]), CLASS_A, "widget-2", ALT_NS),
    ("D class not in allclasses",
     dict(allclasses=[CLASS_B]), CLASS_A, URIRef("http://example.org/inst/1"), None),
    ("E instance is neither URIRef nor string",
     dict(allclasses=[CLASS_A]), CLASS_A, 42, None),
    ("F empty string instance",
     dict(allclasses=[CLASS_A]), CLASS_A, "", None),
]

verdict = {"example": HERE.name, "equivalent": False,
           "method": "entry:instanceAddForClass (hand-rolled: self.sessionGraph "
                     "compared by isomorphism, result/error by equality)",
           "diffs": [], "error": None}

try:
    ns_o, out_o = _exec_python(HERE / "original.py")
    ns_t, out_t = _exec_ldpy(HERE / "translated.ldpy")
    fo = ns_o.get("instanceAddForClass")
    ft = ns_t.get("instanceAddForClass")
    OntologyContext_o = ns_o.get("OntologyContext")
    OntologyContext_t = ns_t.get("OntologyContext")
    if not callable(fo) or not callable(ft):
        raise RuntimeError("entry point not found in both modules")
    if OntologyContext_o is None or OntologyContext_t is None:
        raise RuntimeError("OntologyContext not found in both modules")

    diffs: list[str] = []
    for label, ctx_kwargs, aClass, anInstance, ns in CASES:
        self_o = OntologyContext_o(**ctx_kwargs)
        self_t = OntologyContext_t(**ctx_kwargs)

        err_o = err_t = None
        ro = rt = None
        try:
            ro = fo(self_o, aClass, anInstance, ns)
        except Exception as e:                        # noqa: BLE001 - compared, not raised
            err_o = f"{type(e).__name__}: {e}"
        try:
            rt = ft(self_t, aClass, anInstance, ns)
        except Exception as e:                        # noqa: BLE001 - compared, not raised
            err_t = f"{type(e).__name__}: {e}"

        if err_o != err_t:
            diffs.append(f"case[{label}]: outcome differs "
                         f"(original: {err_o!r}, translated: {err_t!r})")
        elif ro != rt:
            diffs.append(f"case[{label}]: result differs ({ro!r} vs {rt!r})")

        if not graphs_isomorphic(self_o.sessionGraph, self_t.sessionGraph):
            diffs.append(f"case[{label}]: sessionGraph not isomorphic "
                         f"({len(self_o.sessionGraph)} vs {len(self_t.sessionGraph)} triples)")

    if out_o != out_t:
        diffs.append(f"stdout differs ({out_o[:200]!r} vs {out_t[:200]!r})")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    verdict["calls"] = len(CASES)
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

_emit(verdict)
VERDICT = verdict

"""Validation driver for cognitedata__neat__cognite_neat__v0_core__data_model_exporters__data_model2semantic_model.py__OWLClass_title_triples.

The region is a @property body lifted out of its pydantic class, so `demo`
(identical on both sides, see meta.json) attaches it to a minimal
reconstruction of OWLClass with ``OWLClass.title_triples = title_triples``
and reads the property off a fresh instance.

That assignment writes to the class object itself.  With the generic
run_pair, both modules import the SAME context_shim (one entry in
sys.modules), hence the SAME OWLClass: the translated module's assignment
overwrote the original's, both ``demo`` read the translated property, and the
check compared the translation with itself.  This driver therefore drops
context_shim from sys.modules before executing each side, so that each side
imports its own copy of the shim and attaches its property to its own
OWLClass; it asserts that the two classes are distinct objects and that each
side's ``title_triples`` is the function defined in its own file, before
comparing anything.

The oracle is value equality on the returned triple list (RDF terms, not raw
reprs: a Literal's datatype and language are compared).  Inputs are the types
the real repository passes (data_model2semantic_model.py:163-169, 171-190):
``id_`` a URIRef built as ``namespace[suffix]`` (namespace ending in '#' or
'/', and a '#_' separator is handled by remove_namespace_from_uri), ``label``
a ``str | None``.  Cases: a '#' namespace and a '/' namespace and a '#_'
namespace (three branches of the shim's remove_namespace_from_uri, whose
result lands in the Literal), a non-ASCII label, a multi-word label, and the
two falsy labels None and "" (both take the early ``return []``).
A label that is not a str ({"k": 1}: truthy, formatted by the
f-string) is a seventh case.  A raise would be compared too (type and message)
through harness._outcome.
"""
import contextlib
import io
import sys
import traceback
from pathlib import Path

from rdflib import URIRef

from rdfeval import harness

ex_dir = Path(__file__).resolve().parent

CASES = [
    (URIRef("http://example.org/ns#Widget"), "Widget"),
    (URIRef("http://example.org/ns/Widget"), "A widget, with  spaces"),
    (URIRef("http://example.org/ns#_Widget"), "Gadget"),
    (URIRef("http://example.org/ns#Widget"), "Équipement électrique"),
    (URIRef("http://example.org/ns#Widget"), None),
    (URIRef("http://example.org/ns#Widget"), ""),
    (URIRef("http://example.org/ns#Widget"), {"k": 1}),
]


def _load(filename, name):
    """Execute one side with its own, freshly imported context_shim."""
    sys.modules.pop("context_shim", None)
    return harness._exec_artefact(ex_dir / filename, name)


verdict: dict = {"example": ex_dir.name, "equivalent": False,
                 "method": "entry:demo (separate shim per side)",
                 "diffs": [], "error": None}
try:
    left, right = harness.sides_from_env()
    ns_o, out_o = _load(left, "__original__")
    ns_t, out_t = _load(right, "__translated__")
    diffs: list = []
    cls_o, cls_t = ns_o["OWLClass"], ns_t["OWLClass"]
    if cls_o is cls_t:
        diffs.append("both sides share one OWLClass: the second load overwrote "
                     "the first side's title_triples (hollow comparison)")
    if cls_o.__dict__["title_triples"].fget is not ns_o["title_triples"].fget:
        diffs.append("original side: OWLClass.title_triples is not its own property")
    if cls_t.__dict__["title_triples"].fget is not ns_t["title_triples"].fget:
        diffs.append("translated side: OWLClass.title_triples is not its own property")
    for i, (id_, label) in enumerate(CASES):
        outs = []
        for ns in (ns_o, ns_t):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                outs.append(harness._outcome(ns["demo"], (id_, label), {}))
        ro, rt = outs
        if isinstance(ro, harness.Raised) or isinstance(rt, harness.Raised):
            if ro != rt:
                diffs.append(f"call[{i}]: outcome differs ({ro!r} vs {rt!r})")
        else:
            harness._compare_value(ro, rt, f"call[{i}].result", diffs, True)
            if i not in (4, 5) and len(ro) != 1:
                diffs.append(f"call[{i}]: expected one title triple, got {ro!r}")
            if i in (4, 5) and ro != []:
                diffs.append(f"call[{i}]: expected [] for a falsy label, got {ro!r}")
    if out_o != out_t:
        diffs.append("stdout differs at module level")
    verdict["calls"] = len(CASES)
    verdict["observed"] = True
    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
except Exception:
    verdict["error"] = traceback.format_exc(limit=8)

harness._emit(verdict)
VERDICT = verdict

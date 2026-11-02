"""Validation driver for ReproNim__ants_seg_to_nidm__ants_seg_to_nidm_ants_seg_to_nidm.py__add_seg_data.

The region is one module-level statement, `sio = Namespace(Constants.SIO)`;
the rest of ants_seg_to_nidm.py then USES `sio` as an object (`sio.Identifier`
style attribute access, `sio["..."]`, `g.bind("sio", sio)`). Comparing the
module value with `==` is not enough: a Namespace is a `str`, so a bare string
or a URIRef with the same text is `==` to it. So, besides run_pair's module
state comparison, the driver compares a probe of `sio` as the later code
uses it:

  * its type (Namespace, not str/URIRef);
  * `str(sio)`, item access `sio["Identifier"]` (value AND type: a bare str
    raises TypeError, a URIRef gives a different IRI), `sio.term("x")`;
  * `graph.bind("sio", sio)` then the namespace table and a triple minted
    through it, serialised.

An exception raised by one use is part of the probe. The IRI comes from
`Constants.SIO` (a computed value, through the shim), not from a literal in
the region: a translation that hard-codes another IRI is caught.
"""
import contextlib
import io
import sys
from pathlib import Path

from rdflib import Graph, Literal

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent


def _bound(ns):
    graph = Graph()
    graph.bind("sio", ns)
    graph.add((ns["node"], ns["Identifier"], Literal("seg")))
    return (sorted((p, str(u)) for p, u in graph.namespaces() if p == "sio"),
            sorted(graph.serialize(format="nt").splitlines()))


def _probe(ns):
    uses = {
        "type": lambda: type(ns).__module__ + "." + type(ns).__qualname__,
        "str": lambda: str(ns),
        "item": lambda: (str(ns["Identifier"]), type(ns["Identifier"]).__name__),
        "term": lambda: (str(ns.term("x")), type(ns.term("x")).__name__),
        "bind": lambda: _bound(ns),
    }
    out = {}
    for name, use in uses.items():
        try:
            out[name] = use()
        except Exception as e:                    # noqa: BLE001 - part of the probe
            out[name] = ("raised", type(e).__name__)
    return out


# 1. run_pair's verdict (module values, stdout), its own line held back.
with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry=None, calls=None)

# 2. the probe of `sio`, on a second run of each side.
if VERDICT.get("error") is None:
    try:
        sys.modules.pop("context_shim", None)
        ns_o, _ = harness._exec_python(HERE / "original.py")
        sys.modules.pop("context_shim", None)
        ns_t, _ = harness._exec_ldpy(HERE / "translated.ldpy")
        if "sio" not in ns_o or "sio" not in ns_t:
            VERDICT["diffs"].append(
                f"`sio` missing: original {'sio' in ns_o}, translation {'sio' in ns_t}")
        else:
            po, pt = _probe(ns_o["sio"]), _probe(ns_t["sio"])
            if po != pt:
                VERDICT["diffs"].append(f"sio probe differs: {po} vs {pt}")
            if po["str"] != "http://semanticscience.org/ontology/sio.owl#":
                VERDICT["diffs"].append(f"original sio IRI unexpected: {po['str']}")
        VERDICT["probe_compared"] = True
    except Exception as e:                        # noqa: BLE001 - reported
        VERDICT["error"] = f"probe: {type(e).__name__}: {e}"
    VERDICT["equivalent"] = not VERDICT["diffs"] and VERDICT["error"] is None

harness._emit(VERDICT)

"""Validation driver for morph-kgc__morph-kgc__src_morph_kgc_mapping_yarrrml.py___translate_yarrrml_to_rml.

The region is a bare for-loop STATEMENT, not a function: it reads three
free names (``yarrrml_mapping``, ``mapping_graph``, ``tm_id_to_norm_tm_ids``)
that a caller elsewhere in the source module supplies. ``rdfeval.harness``'s
generic ``run_pair`` cannot inject those before exec'ing the script, so this
driver seeds them itself — the fixture returned by ``shim.make_fixture()``
plus a fresh ``rdflib.Graph()`` — runs both versions, and compares the
resulting graph by isomorphism (the region's oracle per meta.json).
"""
import json
import sys
import traceback
from pathlib import Path

import rdflib

from rdfeval.harness import graphs_isomorphic
from shim import make_fixture


def _run(path: Path):
    yarrrml_mapping, tm_id_to_norm_tm_ids = make_fixture()
    mapping_graph = rdflib.Graph()
    ns: dict = {
        "__name__": "__mod__",
        "__file__": str(path),
        "yarrrml_mapping": yarrrml_mapping,
        "mapping_graph": mapping_graph,
        "tm_id_to_norm_tm_ids": tm_id_to_norm_tm_ids,
    }
    if path.suffix == ".ldpy":
        from ldpy.transpiler import transpile
        r = transpile(path.read_text(), filename=str(path))
        code = compile(r.code, str(path), "exec")
    else:
        code = compile(path.read_text(), str(path), "exec")
    exec(code, ns)
    return ns["mapping_graph"]


def main() -> None:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "statement:seeded-globals+isomorphism",
                     "diffs": [], "error": None}
    try:
        g_o = _run(ex_dir / "original.py")
        g_t = _run(ex_dir / "translated.ldpy")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
        return

    diffs: list[str] = []
    if not graphs_isomorphic(g_o, g_t):
        diffs.append(f"mapping_graph not isomorphic ({len(g_o)} vs {len(g_t)} triples)")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)


if __name__ == "__main__":
    main()

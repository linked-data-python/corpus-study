"""Validation driver for dice-group__RELD__data_loader.py__create_graph.

create_graph() returns an EMPTY graph whose whole content is its prefix table:
twelve Namespaces bound by name (the second `g.bind("dbo", ...)`, to another
namespace, lands on `dbo1` in rdflib 7.2.1). Two empty graphs are isomorphic
whatever their bindings, so:

  1. run_pair compares the returned graph (its own `bindings_lost` check:
     no binding of the original may be missing from the translation);
  2. the driver then re-runs both sides and compares the namespace tables
     in BOTH directions (an extra or a misnamed binding is a difference too),
     and checks the original's table holds the eleven expected prefixes.
"""
import contextlib
import io
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent

EXPECTED = {
    "reld": "http://reld.dice-research.org/schema/",
    "reldr": "http://reld.dice-research.org/resource/",
    "dbo": "http://dbpedia.org/ontology/",
    "dbo1": "http://dbpedia.org/property/",
    "freebase": "http://rdf.freebase.com/ns",
    "ps": "http://www.wikidata.org/prop/statement/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "dc": "http://purl.org/dc/elements/1.1/",
    "dcterms": "http://purl.org/dc/terms/",
    "nif": "http://persistence.uni-leipzig.org/nlp2rdf/ontologies/nif-core#",
    "prov": "http://www.w3.org/ns/prov#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
}

with contextlib.redirect_stderr(io.StringIO()):
    VERDICT = run_pair(__file__, entry='create_graph', calls=[((), {})])

if VERDICT.get("error") is None:
    try:
        ns_o, _ = harness._exec_python(HERE / "original.py")
        ns_t, _ = harness._exec_ldpy(HERE / "translated.ldpy")
        table_o = {(p, str(n)) for p, n in ns_o["create_graph"]().namespaces()}
        table_t = {(p, str(n)) for p, n in ns_t["create_graph"]().namespaces()}
        if table_o != table_t:
            VERDICT["diffs"].append(
                f"namespace tables differ: only original {sorted(table_o - table_t)}, "
                f"only translation {sorted(table_t - table_o)}")
        missing = {(p, n) for p, n in EXPECTED.items()} - table_o
        if missing:
            VERDICT["diffs"].append(f"original lacks expected bindings {sorted(missing)}")
        VERDICT["tables_compared"] = True
    except Exception as e:                        # noqa: BLE001 - reported
        VERDICT["error"] = f"table check: {type(e).__name__}: {e}"
    VERDICT["equivalent"] = not VERDICT["diffs"] and VERDICT["error"] is None

harness._emit(VERDICT)

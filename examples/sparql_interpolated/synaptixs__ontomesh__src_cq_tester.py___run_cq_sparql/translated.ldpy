# Extracted from synaptixs/ontomesh@f771c8c4ee : src/cq_tester.py
# region: _run_cq_sparql (lines 361-378, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from typing import List, Dict, Tuple
_CQ_SPARQL_PREFIXES = "\n".join([
    "PREFIX :     <https://ontology.example.com/enterprise/>",
    "PREFIX owl:  <http://www.w3.org/2002/07/owl#>",
    "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>",
    "PREFIX prov: <http://www.w3.org/ns/prov#>",
    "PREFIX skos: <http://www.w3.org/2004/02/skos/core#>",
    "",
])

def _run_cq_sparql(graph, cq) -> Tuple[int, str]:
    """Execute a CQ's SPARQL against the ontology. Returns (rows, status).

    Status mirrors the SQL side: PASS when the row count matches
    `expected_non_empty`, FAIL when it does not, ERROR on a bad query, and
    N/A when no ontology graph could be loaded.
    """
    if graph is None:
        return (0, "N/A")
    query = cq.get("sparql_equiv", "").strip()
    if not query:
        return (0, "N/A")
    try:
        rows = list(graph.query(_CQ_SPARQL_PREFIXES + query))
    except Exception:
        return (0, "ERROR")
    ok = (len(rows) > 0) == cq["expected_non_empty"]
    return (len(rows), "PASS" if ok else "FAIL")

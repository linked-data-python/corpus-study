# Extracted from synaptixs/ontomesh@f771c8c4ee : src/materializer.py
# region: explain_triple (lines 642-685, stratum trav_one_step)
# licence of the source repository: see meta.json
import json
import os
from typing import Any, Dict, List
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import PROV, RDF
from helpers import _parse_term
TOOLKIT_NS = Namespace("https://ontology.example.com/toolkit/materializer/")

def explain_triple(lineage_path: str, subject: str, predicate: str,
                   obj: str) -> List[Dict[str, Any]]:
    """Look up reified-statement records for a given triple. Used by the
    wizard's `/api/explain` endpoint to power the Materialised tab.

    Returns a list of dicts (one per derivation): {rule, engine,
    bindings, premises}. An empty list means the triple is asserted (no
    lineage block exists for it) — the caller should display "asserted".
    """
    if not os.path.isfile(lineage_path):
        return []
    g = Graph().parse(lineage_path, format="turtle")
    s = URIRef(subject)
    p = URIRef(predicate)
    o = _parse_term(obj)

    out: List[Dict[str, Any]] = []
    for stmt in g.subjects(RDF.type, RDF.Statement):
        if ((stmt, RDF.subject, s) not in g or (stmt, RDF.predicate, p) not in g
                or (stmt, RDF.object, o) not in g):
            continue
        for deriv in g.objects(stmt, PROV.wasDerivedFrom):
            rule = g.value(deriv, TOOLKIT_NS.rule)
            engine = g.value(deriv, TOOLKIT_NS.engine)
            bindings = g.value(deriv, TOOLKIT_NS.bindings)
            try:
                bindings_obj = json.loads(str(bindings)) if bindings else {}
            except Exception:
                bindings_obj = {}
            premises = [[g.value(prem, term) for term in (RDF.subject, RDF.predicate, RDF.object)]
                        for prem in g.objects(deriv, TOOLKIT_NS.premise)]
            out.append({
                "rule": str(rule) if rule else None,
                "engine": str(engine) if engine else None,
                "bindings": bindings_obj,
                "premises": [list(map(str, premise)) for premise in premises if all(premise)],
            })
    return out

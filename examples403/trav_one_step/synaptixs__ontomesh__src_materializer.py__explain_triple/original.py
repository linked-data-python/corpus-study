# Extracted from synaptixs/ontomesh@f771c8c4ee : src/materializer.py
# region: explain_triple (lines 642-685, stratum trav_one_step)
# licence of the source repository: see meta.json
import json
import os
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from rdflib import BNode, Graph, Literal, Namespace, URIRef, Variable
from rdflib.namespace import OWL, PROV, RDF, RDFS, XSD
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
    g = Graph()
    g.parse(lineage_path, format="turtle")
    s = URIRef(subject)
    p = URIRef(predicate)
    o = _parse_term(obj)

    out: List[Dict[str, Any]] = []
    for stmt in g.subjects(RDF.type, RDF.Statement):
        if (stmt, RDF.subject, s) not in g: continue
        if (stmt, RDF.predicate, p) not in g: continue
        if (stmt, RDF.object, o) not in g: continue
        for _, _, deriv in g.triples((stmt, PROV.wasDerivedFrom, None)):
            rule = next(g.objects(deriv, TOOLKIT_NS.rule), None)
            engine = next(g.objects(deriv, TOOLKIT_NS.engine), None)
            bindings = next(g.objects(deriv, TOOLKIT_NS.bindings), None)
            try:
                bindings_obj = json.loads(str(bindings)) if bindings else {}
            except Exception:
                bindings_obj = {}
            premises = []
            for _, _, prem in g.triples((deriv, TOOLKIT_NS.premise, None)):
                ps = next(g.objects(prem, RDF.subject), None)
                pp = next(g.objects(prem, RDF.predicate), None)
                po = next(g.objects(prem, RDF.object), None)
                if ps and pp and po:
                    premises.append([str(ps), str(pp), str(po)])
            out.append({
                "rule": str(rule) if rule else None,
                "engine": str(engine) if engine else None,
                "bindings": bindings_obj,
                "premises": premises,
            })
    return out

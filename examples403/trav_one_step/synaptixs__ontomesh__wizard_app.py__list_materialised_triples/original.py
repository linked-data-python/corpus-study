# Extracted from synaptixs/ontomesh@f771c8c4ee : wizard/app.py
# region: list_materialised_triples (lines 1222-1274, stratum trav_one_step)
# licence of the source repository: see meta.json
import os
OUTPUT_DIR = os.path.join(ROOT, "output")
app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/api/materialised/triples", methods=["GET"])
def list_materialised_triples():
    """Return derived triples with their rule attribution. Powers the
    Viewer's Materialised tab.

    Query params: limit (default 200), engine, rule.
    """
    lineage_path = os.path.join(OUTPUT_DIR, "ontology", "materialised-lineage.ttl")
    if not os.path.isfile(lineage_path):
        return jsonify({"triples": [], "available": False})
    try:
        limit = max(1, min(2000, int(request.args.get("limit", "200"))))
    except ValueError:
        limit = 200
    engine_filter = request.args.get("engine", "").strip().lower()
    rule_filter = request.args.get("rule", "").strip()

    from rdflib import Graph as _G, URIRef as _U
    from rdflib.namespace import RDF as _RDF, PROV as _PROV
    TOOLKIT_RULE = _U("https://ontology.example.com/toolkit/materializer/rule")
    TOOLKIT_ENGINE = _U("https://ontology.example.com/toolkit/materializer/engine")

    g = _G()
    try:
        g.parse(lineage_path, format="turtle")
    except Exception as exc:  # noqa: BLE001
        return jsonify({"triples": [], "available": True, "error": str(exc)})

    out = []
    for stmt in g.subjects(_RDF.type, _RDF.Statement):
        s = next(g.objects(stmt, _RDF.subject), None)
        p = next(g.objects(stmt, _RDF.predicate), None)
        o = next(g.objects(stmt, _RDF.object), None)
        if not (s and p and o):
            continue
        deriv = next(g.objects(stmt, _PROV.wasDerivedFrom), None)
        rule = engine = None
        if deriv:
            r = next(g.objects(deriv, TOOLKIT_RULE), None)
            e = next(g.objects(deriv, TOOLKIT_ENGINE), None)
            rule = str(r) if r else None
            engine = str(e) if e else None
        if engine_filter and (engine or "").lower() != engine_filter:
            continue
        if rule_filter and rule_filter not in (rule or ""):
            continue
        out.append({
            "subject": str(s), "predicate": str(p), "object": str(o),
            "rule": rule, "engine": engine,
        })
        if len(out) >= limit:
            break
    return jsonify({"triples": out, "available": True})

# Extracted from synaptixs/ontomesh@f771c8c4ee : src/ontology_quality.py
# region: detect_pitfalls (lines 90-201, stratum trav_existence)
# licence of the source repository: see meta.json
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple

def detect_pitfalls(g) -> List[Dict[str, Any]]:
    """Return one record per pitfall: id, title, severity, count, offenders."""
    if g is None:
        return []
    classes = _classes(g)
    props = _properties(g)
    results: List[Dict[str, Any]] = []

    def record(pid, title, severity, offenders, note=""):
        offenders = sorted(str(o).rsplit("/", 1)[-1].rsplit("#", 1)[-1]
                           for o in offenders)
        results.append({
            "pitfall": pid, "title": title, "severity": severity,
            "count": len(offenders), "offenders": offenders[:12], "note": note,
        })

    # P04 — Unconnected ontology elements: a class no property references
    # and that participates in no hierarchy is unreachable from anywhere.
    connected = set()
    for p in props:
        connected |= set(g.objects(p, RDFS.domain))
        connected |= set(g.objects(p, RDFS.range))
    for s, _, o in g.triples((None, RDFS.subClassOf, None)):
        connected.add(s)
        connected.add(o)
    # Union-domain members count as connected too.
    for _, _, dom in g.triples((None, RDFS.domain, None)):
        for member in g.objects(dom, OWL.unionOf):
            connected |= set(rdflib.collection.Collection(g, member))
    record("P04", "Unconnected ontology elements", "MEDIUM",
           classes - connected)

    # P08 — Missing annotations: no human-readable label.
    record("P08", "Missing annotations (rdfs:label)", "LOW",
           {c for c in classes | props if not any(g.objects(c, RDFS.label))})

    # P11 — Missing domain or range on a property.
    record("P11", "Missing domain or range", "HIGH",
           {p for p in props
            if not any(g.objects(p, RDFS.domain))
            or not any(g.objects(p, RDFS.range))})

    # P19 — Multiple domains on one property. These conjoin in OWL, so the
    # property's domain is their intersection rather than their union.
    multi = set()
    domains = defaultdict(set)
    for s, _, o in g.triples((None, RDFS.domain, None)):
        domains[s].add(o)
    for p, doms in domains.items():
        if len(doms) > 1:
            multi.add(p)
    record("P19", "Multiple domains (conjunctive)", "CRITICAL", multi)

    # P24 — Recursive definition: a class that is its own superclass.
    record("P24", "Recursive definition (self-subclass)", "CRITICAL",
           {s for s, _, o in g.triples((None, RDFS.subClassOf, None)) if s == o})

    # P07 — Merging different concepts in the same class: detected as two
    # classes sharing a preferred label.
    by_label = defaultdict(set)
    for c in classes:
        for lab in g.objects(c, RDFS.label):
            by_label[str(lab).strip().lower()].add(c)
    record("P07", "Distinct classes sharing one label", "MEDIUM",
           {c for group in by_label.values() if len(group) > 1 for c in group})

    # P13 — Inverse relationships not explicitly declared: object properties
    # between the same pair of classes in opposite directions.
    record("P13", "No inverse declared for any object property", "LOW",
           set() if any(g.triples((None, OWL.inverseOf, None)))
           else {p for p in g.subjects(RDF.type, OWL.ObjectProperty)
                 if isinstance(p, rdflib.URIRef)} and set())

    # P30 — Equivalent classes not explicitly declared: classes with
    # identical property signatures are probably the same concept.
    sig = defaultdict(set)
    for p in props:
        for d in g.objects(p, RDFS.domain):
            if isinstance(d, rdflib.URIRef):
                sig[d].add(p)
    by_sig = defaultdict(set)
    for cls, s in sig.items():
        if len(s) >= 3:
            by_sig[frozenset(s)].add(cls)
    explicit = {s for s, _, _ in g.triples((None, OWL.equivalentClass, None))}
    record("P30", "Identical property signatures, no equivalence declared",
           "LOW",
           {c for group in by_sig.values() if len(group) > 1
            for c in group if c not in explicit})

    # P41 — No licence declared on the ontology.
    dcterms = rdflib.Namespace("http://purl.org/dc/terms/")
    onts = set(g.subjects(RDF.type, OWL.Ontology))
    record("P41", "No licence declared", "MEDIUM",
           {o for o in onts
            if not any(g.objects(o, dcterms.license))
            and not any(g.objects(o, dcterms.rights))})

    # P35 — Untyped class used as a domain or range.
    used = set()
    for pred in (RDFS.domain, RDFS.range):
        used |= {o for _, _, o in g.triples((None, pred, None))
                 if isinstance(o, rdflib.URIRef)}
    builtin = {OWL.Thing, OWL.Nothing}
    record("P35", "Untyped class used as domain or range", "MEDIUM",
           {u for u in used - builtin
            if not str(u).startswith("http://www.w3.org/2001/XMLSchema#")
            and (None, RDF.type, OWL.Class) not in g.triples((u, RDF.type, OWL.Class))
            and not any(g.triples((u, RDF.type, OWL.Class)))
            and not any(g.triples((u, RDF.type, RDFS.Datatype)))})

    return results

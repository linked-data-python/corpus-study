# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe/evaluation/aspects/func/validator_rdflib.py
# region: check_domain_violations (lines 27-34, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal

def check_domain_violations(g: Graph):
    violations = []
    for prop in set(g.subjects(RDF.type, RDF.Property)).union(g.subjects(RDF.type, OWL.ObjectProperty)):
        for s, p, o in g.triples((None, prop, None)):
            for _, _, domain in g.triples((prop, RDFS.domain, None)):
                if not (s, RDF.type, domain) in g:
                    violations.append((s, prop, "Expected domain", domain))
    return violations

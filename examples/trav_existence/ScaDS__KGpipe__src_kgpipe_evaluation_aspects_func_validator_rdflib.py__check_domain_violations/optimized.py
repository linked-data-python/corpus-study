# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe/evaluation/aspects/func/validator_rdflib.py
# region: check_domain_violations (lines 27-34, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal

def check_domain_violations(g: Graph):
    return [(s, prop, "Expected domain", domain)
            for prop in set(g.subjects(RDF.type, RDF.Property)).union(
                g.subjects(RDF.type, OWL.ObjectProperty))
            for s in g.subjects(prop)
            for domain in g.objects(prop, RDFS.domain)
            if (s, RDF.type, domain) not in g]

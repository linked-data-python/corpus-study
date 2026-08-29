# Extracted from spdx/spec-parser@47ef6b7c04 : spec_parser/rdf.py
# region: gen_rdf_properties (lines 193-219, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, SKOS, XSD

def gen_rdf_properties(model, g):
    for fqname, p in model.properties.items():
        if fqname == "/Core/spdxId":
            continue
        node = URIRef(p.iri)
        if p.summary:
            g.add((node, RDFS.comment, Literal(p.summary, lang="en")))
        if p.metadata["Nature"] == "ObjectProperty":
            g.add((node, RDF.type, OWL.ObjectProperty))
        # to add: g.add((node, RDFS.domain, xxx))
        elif p.metadata["Nature"] == "DataProperty":
            g.add((node, RDF.type, OWL.DatatypeProperty))
        rng = p.metadata["Range"]
        if ":" in rng:
            t = xsd_range(rng, p.name)
            if t:
                g.add((node, RDFS.range, t))
        else:
            typename = "" if rng.startswith("/") else f"/{p.ns.name}/"
            typename += rng
            if typename in model.datatypes:
                t = xsd_range(model.datatypes[typename].metadata["SubclassOf"], p.name)
                if t:
                    g.add((node, RDFS.range, t))
            else:
                dt = model.types[typename]
                g.add((node, RDFS.range, URIRef(dt.iri)))

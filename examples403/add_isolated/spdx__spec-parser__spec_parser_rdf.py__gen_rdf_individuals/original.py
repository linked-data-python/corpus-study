# Extracted from spdx/spec-parser@47ef6b7c04 : spec_parser/rdf.py
# region: gen_rdf_individuals (lines 236-259, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, SKOS, XSD
URI_BASE = "https://spdx.org/rdf/3/terms/"

def gen_rdf_individuals(model, g):
    def ci_ref(s):
        return URIRef(URI_BASE + "Core/" + s)

    for i in model.individuals.values():
        ci_node = URIRef("https://spdx.org/rdf/3.1/creationInfo_" + i.name)
        g.add((ci_node, RDF.type, ci_ref("CreationInfo")))
        g.add((ci_node, RDFS.comment, Literal("This individual element was defined by the spec.", lang="en")))
        g.add((ci_node, ci_ref("created"), Literal("2026-01-23T03:01:00Z", datatype=XSD.dateTimeStamp)))
        g.add((ci_node, ci_ref("createdBy"), ci_ref("SpdxOrganization")))
        g.add((ci_node, ci_ref("specVersion"), Literal("3.1")))
        node = URIRef(i.iri)
        g.add((node, RDF.type, OWL.NamedIndividual))
        g.add((node, ci_ref("creationInfo"), ci_node))
        if i.summary:
            g.add((node, RDFS.comment, Literal(i.summary, lang="en")))
        typ = i.metadata["type"]
        typename = "" if typ.startswith("/") else f"/{i.ns.name}/"
        typename += typ
        dt = model.types[typename]
        g.add((node, RDF.type, URIRef(dt.iri)))
        custom_iri = i.metadata.get("IRI")
        if custom_iri and custom_iri != i.iri:
            g.add((node, OWL.sameAs, URIRef(custom_iri)))

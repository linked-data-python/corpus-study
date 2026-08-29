# Extracted from spdx/spec-parser@47ef6b7c04 : spec_parser/rdf.py
# region: gen_rdf_ontology (lines 43-76, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib import BNode, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, OWL, RDF, RDFS, SH, SKOS, XSD
URI_BASE = "https://spdx.org/rdf/3/terms/"

def gen_rdf_ontology(model):
    g = Graph()
    g.bind("spdx", Namespace(URI_BASE))
    OMG_ANN = Namespace("https://www.omg.org/spec/Commons/AnnotationVocabulary/")
    g.bind("omg-ann", OMG_ANN)

    node = URIRef(URI_BASE)
    g.add((node, RDF.type, OWL.Ontology))
    g.add((node, OWL.versionIRI, node))
    g.add((node, RDFS.label, Literal("System Package Data Exchange™ (SPDX®) Ontology", lang="en")))
    g.add(
        (
            node,
            DCTERMS.abstract,
            Literal(
                "This ontology defines the terms and relationships used in the SPDX specification to describe system packages",
                lang="en",
            ),
        ),
    )
    g.add((node, DCTERMS.created, Literal("2026-01-23", datatype=XSD.date)))
    g.add((node, DCTERMS.creator, Literal("SPDX Project", lang="en")))
    g.add((node, DCTERMS.license, URIRef("https://spdx.org/licenses/Community-Spec-1.0.html")))
    g.add((node, DCTERMS.references, URIRef("https://spdx.dev/specifications/")))
    g.add((node, DCTERMS.title, Literal("System Package Data Exchange (SPDX) Ontology", lang="en")))
    g.add((node, OMG_ANN.copyright, Literal("Copyright (C) 2026 SPDX Project", lang="en")))

    gen_rdf_classes(model, g)
    gen_rdf_properties(model, g)
    #     gen_rdf_datatypes(model, g)
    gen_rdf_vocabularies(model, g)
    gen_rdf_individuals(model, g)

    return g

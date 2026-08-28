# Extracted from RDFLib/VocPrez@ce3c0ea42f : vocprez/model/concept.py
# region: ConceptRenderer._render_skos_rdf (lines 59-113, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from flask import Response, render_template, g
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS
import vocprez._config as config

def _render_skos_rdf(self):
    g = Graph()
    g.bind("dct", DCTERMS)
    g.bind("skos", SKOS)

    cs = URIRef(self.concept.vocab_uri)
    g.bind("cs", cs)
    c = URIRef(self.concept.uri)
    g.bind("", "/".join(str(c).split("/")[:-1]) + "/")

    # Concept SKOS metadata
    g.add((
        c,
        RDF.type,
        SKOS.Concept
    ))
    g.add((
        c,
        SKOS.prefLabel,
        Literal(self.concept.prefLabel, lang=config.DEFAULT_LANGUAGE)
    ))
    g.add((
        c,
        SKOS.definition,
        Literal(self.concept.definition, lang=config.DEFAULT_LANGUAGE)
    ))
    g.add((c, SKOS.inScheme, cs))

    if self.concept.related_instances is not None:
        for k, v in self.concept.related_instances.items():
            for prop in v:
                if str(prop.value).startswith("http"):
                    g.add((c, URIRef(prop.uri), URIRef(prop.value)))
                else:
                    g.add((c, URIRef(prop.uri), Literal(prop.value)))

    if self.concept.other_properties is not None:
        for v in self.concept.other_properties:
            for prop in v:
                if str(prop.value).startswith("http"):
                    g.add((c, URIRef(prop.uri), URIRef(prop.value)))
                else:
                    g.add((c, URIRef(prop.uri), Literal(prop.value)))

    # serialise in the appropriate RDF format
    if self.mediatype in ["application/ld+json", "application/json"]:
        graph_text = g.serialize(format="turtle")
    else:
        graph_text = g.serialize(format=self.mediatype)

    return Response(
        graph_text,
        mimetype=self.mediatype,
        headers=self.headers,
    )

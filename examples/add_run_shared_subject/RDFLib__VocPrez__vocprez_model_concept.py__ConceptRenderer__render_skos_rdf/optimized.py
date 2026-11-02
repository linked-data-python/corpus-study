# Extracted from RDFLib/VocPrez@ce3c0ea42f : vocprez/model/concept.py
# region: ConceptRenderer._render_skos_rdf (lines 59-113, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from flask import Response, render_template, g
from rdflib import Graph, URIRef, Literal
from rdflib.namespace import DCTERMS, RDF, RDFS, SKOS
import vocprez._config as config

def _render_skos_rdf(self):
    concept = self.concept
    g = Graph()
    g.bind("dct", DCTERMS)
    g.bind("skos", SKOS)

    cs = URIRef(concept.vocab_uri)
    g.bind("cs", cs)
    c = URIRef(concept.uri)
    g.bind("", str(c).rpartition("/")[0] + "/")

    # Concept SKOS metadata
    g.add((c, RDF.type, SKOS.Concept))
    g.add((c, SKOS.prefLabel, Literal(concept.prefLabel, lang=config.DEFAULT_LANGUAGE)))
    g.add((c, SKOS.definition, Literal(concept.definition, lang=config.DEFAULT_LANGUAGE)))
    g.add((c, SKOS.inScheme, cs))

    for v in [*(concept.related_instances or {}).values(), *(concept.other_properties or [])]:
        for prop in v:
            value = URIRef(prop.value) if str(prop.value).startswith("http") else Literal(prop.value)
            g.add((c, URIRef(prop.uri), value))

    # serialise in the appropriate RDF format
    is_json = self.mediatype in ["application/ld+json", "application/json"]
    graph_text = g.serialize(format="turtle" if is_json else self.mediatype)
    return Response(graph_text, mimetype=self.mediatype, headers=self.headers)

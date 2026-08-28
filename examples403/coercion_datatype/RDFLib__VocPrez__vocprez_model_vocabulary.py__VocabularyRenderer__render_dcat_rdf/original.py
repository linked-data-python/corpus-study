# Extracted from RDFLib/VocPrez@ce3c0ea42f : vocprez/model/vocabulary.py
# region: VocabularyRenderer._render_dcat_rdf (lines 100-155, stratum coercion_datatype)
# licence of the source repository: see meta.json
from flask import Response, render_template
from rdflib import Graph, URIRef, Literal, XSD, RDF
from rdflib.namespace import DCTERMS, OWL, SKOS, Namespace, NamespaceManager

def _render_dcat_rdf(self):
    # get vocab RDF
    g = Graph()
    # map nice prefixes to namespaces
    NamespaceManager(g)
    DCAT = Namespace("https://www.w3.org/ns/dcat#")
    g.namespace_manager.bind("dcat", DCAT)
    g.namespace_manager.bind("dct", DCTERMS)
    g.namespace_manager.bind("owl", OWL)
    g.namespace_manager.bind("skos", SKOS)
    s = URIRef(self.vocab.uri)

    g.add((s, RDF.type, DCAT.Dataset))
    if self.vocab.title:
        g.add((s, DCTERMS.title, Literal(self.vocab.title)))
    if self.vocab.description:
        g.add((s, DCTERMS.description, Literal(self.vocab.description)))
    if self.vocab.creator:
        if (
            self.vocab.creator[:7] == "http://"
            or self.vocab.creator[:7] == "https://"
        ):  # if url
            g.add((s, DCTERMS.creator, URIRef(self.vocab.creator)))
        else:  # else literal
            g.add((s, DCTERMS.creator, Literal(self.vocab.creator)))
    if self.vocab.created:
        g.add((s, DCTERMS.created, Literal(self.vocab.created, datatype=XSD.date)))
    if self.vocab.modified:
        g.add(
            (s, DCTERMS.modified, Literal(self.vocab.modified, datatype=XSD.date))
        )
    if self.vocab.versionInfo:
        g.add((s, OWL.versionInfo, Literal(self.vocab.versionInfo)))
    if self.vocab.accessURL:
        g.add((s, DCAT.accessURL, URIRef(self.vocab.accessURL)))
    if self.vocab.downloadURL:
        g.add((s, DCAT.downloadURL, URIRef(self.vocab.downloadURL)))

    sp = URIRef(SYSTEM_BASE_URI + "/sparql")
    g.add((sp, DCAT.servesDataset, s))
    g.add((sp, DCTERMS.title, Literal("VocPrez SPARQL Service")))
    api = URIRef(SYSTEM_BASE_URI)
    g.add((api, DCAT.servesDataset, s))
    g.add((api, DCTERMS.title, Literal("VocPrez Linked Data API")))

    if self.vocab.other_properties is not None:
        for prop in self.vocab.other_properties:
            # other properties from DCAT, DCTERMS only
            if str(prop.uri).startswith(("https://www.w3.org/ns/dcat#", "http://purl.org/dc/terms/")):
                g.add((s, URIRef(prop.uri), prop.value))

    # serialise in the appropriate RDF format
    if self.mediatype in ["application/rdf+json", "application/json"]:
        return Response(g.serialize(format="json-ld"), mimetype=self.mediatype, headers=self.headers)
    else:
        return Response(g.serialize(format=self.mediatype), mimetype=self.mediatype, headers=self.headers)

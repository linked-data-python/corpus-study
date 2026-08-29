# Extracted from eliozo/worksheet-generation-with-llms@c065efff55 : scripts/rdfgen/csv_to_concepts.py
# region: addToRdfGraph (lines 25-39, stratum coercion_datatype)
# licence of the source repository: see meta.json
import rdflib
eliozo_ns = "http://www.dudajevagatve.lv/eliozo#"
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"

def addToRdfGraph(g, conceptID, termLV, descLV, termEN=None):
    rdf_type_property = rdflib.URIRef(RDF_NS + 'type')
    topic_node = rdflib.URIRef(eliozo_ns + "TRM-" + conceptID)
    g.add((topic_node, rdf_type_property, rdflib.URIRef(eliozo_ns + "Concept")))
    if not termEN:
        termEN = conceptID.replace("-", " ")
    termEN_property = rdflib.URIRef(eliozo_ns + 'termEN')
    termLV_property = rdflib.URIRef(eliozo_ns + 'termLV')
    descLV_property = rdflib.URIRef(eliozo_ns + 'descLV')
    conceptID_property = rdflib.URIRef(eliozo_ns + 'conceptID')
    g.add((topic_node, termEN_property, rdflib.term.Literal(termEN, lang=u'en')))
    g.add((topic_node, termLV_property, rdflib.term.Literal(termLV, lang=u'lv')))
    g.add((topic_node, conceptID_property, rdflib.term.Literal(conceptID, lang=u'en')))
    if descLV and descLV != "" and descLV != "NA":
        g.add((topic_node, descLV_property, rdflib.term.Literal(descLV, lang=u'lv')))

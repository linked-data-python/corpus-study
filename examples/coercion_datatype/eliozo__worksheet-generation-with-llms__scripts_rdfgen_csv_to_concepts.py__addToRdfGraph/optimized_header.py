# Extracted from eliozo/worksheet-generation-with-llms@c065efff55 : scripts/rdfgen/csv_to_concepts.py
# region: addToRdfGraph (lines 25-39, stratum coercion_datatype)
# licence of the source repository: see meta.json
import rdflib
eliozo_ns = "http://www.dudajevagatve.lv/eliozo#"

def addToRdfGraph(g, conceptID, termLV, descLV, termEN=None):
    eliozo = rdflib.Namespace(eliozo_ns)
    topic_node = eliozo["TRM-" + conceptID]
    if not termEN:
        termEN = conceptID.replace("-", " ")
    g += [
        (topic_node, rdflib.RDF.type, eliozo.Concept),
        (topic_node, eliozo.termEN, rdflib.Literal(termEN, lang='en')),
        (topic_node, eliozo.termLV, rdflib.Literal(termLV, lang='lv')),
        (topic_node, eliozo.conceptID, rdflib.Literal(conceptID, lang='en')),
    ]
    if descLV and descLV != "NA":
        g.add((topic_node, eliozo.descLV, rdflib.Literal(descLV, lang='lv')))

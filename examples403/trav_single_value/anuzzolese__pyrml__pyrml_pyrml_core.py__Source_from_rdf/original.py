# Extracted from anuzzolese/pyrml@d18fe2edfc : pyrml/pyrml_core.py
# region: Source.from_rdf (lines 1770-1795, stratum trav_single_value)
# licence of the source repository: see meta.json
from pyrml import rml_vocab
from rdflib import URIRef, Graph, IdentifiedNode
from rdflib.namespace import RDF, Namespace, XSD
from rdflib.term import Node, BNode, Literal, Identifier, URIRef, _is_valid_langtag, _castPythonToLiteral, _castLexicalToPython 
import pyrml.rml_vocab as rml_vocab

@staticmethod
def from_rdf(g: Graph, parent: IdentifiedNode) -> 'Source':
    term_maps = []
    sources = g.objects(parent, rml_vocab.RML_NS.source, True)

    for source in sources:

        sourcetype = None

        if isinstance(source, Literal):
            sourcetype = Literal('plain')
        elif g.value(source, rml_vocab.CSVW_NS.url):
            sourcetype = Literal('table')
        elif g.value(source, rml_vocab.SD_NS.endpoint):
            sourcetype = Literal('sparql')
        elif g.value(source, rml_vocab.D2RQ_NS.jdbcDSN):
            sourcetype = Literal('sql')
        else:
            db = g.value(None, RDF.type, rml_vocab.D2RQ_NS.Database, True)
            if db:
                return [SQLSource.from_rdf(g, db)]

        if sourcetype:
            term_maps.append(Source.__build(g, parent, source, sourcetype))

    return term_maps

# Extracted from anuzzolese/pyrml@d18fe2edfc : pyrml/pyrml_core.py
# region: Source.from_rdf (lines 1770-1795, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import Graph, IdentifiedNode
from rdflib.namespace import RDF
from rdflib.term import Literal
from context_shim import rml_vocab, Source, SQLSource  # see meta.json: context shim

@staticmethod
def from_rdf(g: Graph, parent: IdentifiedNode) -> 'Source':
    term_maps = []
    for source in g.objects(parent, rml_vocab.RML_NS.source):
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
            continue
        term_maps.append(Source.__build(g, parent, source, sourcetype))

    return term_maps

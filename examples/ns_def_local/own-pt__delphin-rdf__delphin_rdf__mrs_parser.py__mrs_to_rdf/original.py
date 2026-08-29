# Extracted from own-pt/delphin-rdf@ea21d53844 : delphin/rdf/_mrs_parser.py
# region: mrs_to_rdf (lines 23-67, stratum ns_def_local)
# licence of the source repository: see meta.json
from rdflib.graph import Graph, ConjunctiveGraph
from rdflib import RDF
from rdflib import Namespace
import rdflib
import delphin.mrs
import delphin.variable
import delphin.predicate
MRS = Namespace("http://www.delph-in.net/schema/mrs#")
DELPH = Namespace("http://www.delph-in.net/schema/")

def mrs_to_rdf(m:delphin.mrs._mrs.MRS, 
                MRSI:rdflib.term.URIRef,
                defaultGraph:rdflib.graph.ConjunctiveGraph=None) -> rdflib.graph.ConjunctiveGraph:
    """
    Takes a PyDelphin MRS object "m" and serializes it into a named RDF graph inside a store.

    Args:
        m: a PyDelphin MRS instance to be converted into RDF format
        MRSI: URI of the MRS instance being converted
        defaultGraph : the conjunctive graph representing the profile graph. If not given, creates one.

    Inplace function that alters the conjunctive graph with the serialized MRS and return the conjunctive graph as well.
    In case of using it without giving the graph, it creates one and returns it.
    """
    # Making the arguments behave well:
    if defaultGraph is None:
        defaultGraph = ConjunctiveGraph()

    # MRS graph:
    mrsGraph = Graph(store=defaultGraph.store, identifier=MRSI)

    mrsGraph.add((MRSI, RDF.type, MRS.mrs))

    # Creating the prefix of the MRS elements and relevant namespaces
    insprefix = Namespace(MRSI + '#')
    VARS = Namespace(insprefix + "variable-")
    RELS = Namespace(insprefix + "EP-")
    PREDS = Namespace(insprefix + "predicate-")
    SORTINFO = Namespace(insprefix + "sortinfo-")
    HCONS = Namespace(insprefix + "hcons-")
    ICONS = Namespace(insprefix + "icons-")

    # Adding top and index
    mrsGraph.add((MRSI, RDF.type, MRS.mrs))
    mrsGraph.add((MRSI, DELPH['hasTop'], VARS[m.top]))
    mrsGraph.add((MRSI, DELPH['hasIndex'], VARS[m.index]))
    # ALTERNATIVE: (BNode, DELPH['hasTop'], VARS[m.top])

    # Populating the graphs
    _vars_to_rdf(m, mrsGraph, VARS, SORTINFO)
    _rels_to_rdf(m, mrsGraph, defaultGraph, MRSI, RELS, PREDS, VARS)
    _hcons_to_rdf(m, mrsGraph, defaultGraph, MRSI, HCONS, VARS)
    _icons_to_rdf(m, mrsGraph, defaultGraph, MRSI, ICONS, VARS)

    return defaultGraph

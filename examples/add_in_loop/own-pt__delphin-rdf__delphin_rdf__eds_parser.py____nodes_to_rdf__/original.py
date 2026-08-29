# Extracted from own-pt/delphin-rdf@ea21d53844 : delphin/rdf/_eds_parser.py
# region: __nodes_to_rdf__ (lines 63-125, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Literal
from rdflib import RDF
from rdflib import RDFS
import delphin.eds
import delphin.variable
import delphin.predicate
EDS = Namespace("http://www.delph-in.net/schema/eds#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")
DELPH = Namespace("http://www.delph-in.net/schema/")
POS = Namespace("http://www.delph-in.net/schema/pos#")

def __nodes_to_rdf__(e, edsGraph, defaultGraph, EDSI, NODES, PREDS, SORTINFO):
    """
    Creates in the graphs the nodes of EDS predications and their properties.

    Args:
        e: a PyDelphin EDS instance to be converted into RDF format
        edsGraph: a rdflib Graph where the EDS triples will be put.
        defaultGraph : the conjunctive graph representing the profile graph.
        EDSI: the node of the EDS instance being converted
        NODES: the URI namespace dedicated to EDS predications
        PREDS: the URI namespace dedicated to predicates
        SORTINFO: the URI namespace dedicated to the sortinfo (morphosemantic information).
    """
    for node in e.nodes:
        nodeURI = NODES[node.id]
        predURI = PREDS[node.id]
        sortinfoURI = SORTINFO[node.id]

        edsGraph.add((nodeURI, RDF.type, EDS.Node))

        # Information about the EDS node
        edsGraph.add((EDSI, EDS.hasNode, nodeURI))
        edsGraph.add((nodeURI, DELPH.hasPredicate, predURI))
        edsGraph.add((nodeURI, EDS.nodeIdentifier, Literal(node.id))) # review later if this is useful
        edsGraph.add((nodeURI, RDFS.label, Literal(f"{delphin.predicate.normalize(node.predicate)}<{node.cfrom},{node.cto}>")))
        #type:
        if node.type is not None:
            edsGraph.add((nodeURI, RDF.type, DELPH[node.type]))

        # Information about the predicate
        edsGraph.add((predURI, DELPH.predText, Literal(delphin.predicate.normalize(node.predicate))))
        if delphin.predicate.is_surface(node.predicate):
            edsGraph.add((predURI, RDF.type, DELPH.SurfacePredicate))
        elif delphin.predicate.is_abstract(node.predicate):
            edsGraph.add((predURI, RDF.type, DELPH.AbstractPredicate))
        else: #not surface neither abstract
            edsGraph.add((predURI, RDF.type, DELPH.Predicate))
            print(f"{node.predicate} is an invalid predicate.")

        splittedPredicate = delphin.predicate.split(delphin.predicate.normalize(node.predicate))
        if splittedPredicate[0] is not None: #is this possible?
            edsGraph.add((predURI, DELPH.hasLemma, Literal(splittedPredicate[0])))
        if splittedPredicate[1] is not None:
            edsGraph.add((predURI, DELPH.hasPos, POS[splittedPredicate[1]]))
        if splittedPredicate[2] is not None:
            edsGraph.add((predURI, DELPH.hasSense, Literal(splittedPredicate[2])))

        #lnk:
        if node.cfrom is not None: 
            edsGraph.add((nodeURI, DELPH.cfrom, Literal(node.cfrom)))
        if node.cto is not None:
            edsGraph.add((nodeURI, DELPH.cto, Literal(node.cto)))

        # properties
        if node.properties != {}:
            edsGraph.add((nodeURI, DELPH.hasSortInfo, sortinfoURI))
            edsGraph.add((sortinfoURI, RDF.type, DELPH.SortInfo))
            for prop in node.properties.items():
                edsGraph.add((sortinfoURI, ERG[prop[0].lower()], Literal(prop[1].lower())))

        # carg; review later
        if node.carg:
            edsGraph.add((nodeURI, DELPH.carg, Literal(node.carg)))

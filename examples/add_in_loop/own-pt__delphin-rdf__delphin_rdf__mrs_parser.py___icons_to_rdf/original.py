# Extracted from own-pt/delphin-rdf@ea21d53844 : delphin/rdf/_mrs_parser.py
# region: _icons_to_rdf (lines 180-208, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import RDF
from rdflib import RDFS
MRS = Namespace("http://www.delph-in.net/schema/mrs#")
ERG = Namespace("http://www.delph-in.net/schema/erg#")

def _icons_to_rdf(m, mrsGraph, defaultGraph, MRSI, ICONS, VARS):
    """
    Describes individual constraints "ICONS" in MRS-RDF format

    Args:
        m: a delphin mrs instance to be converted into RDF format
        mrsGraph: a rdflib Graph where the MRS triples will be put.
        defaultGraph: the conjunctive graph of the profile
        MRSI: the node of the MRS instance being converted
        ICONS: the URI namespace dedicated to individual constraints
        VARS: the URI namespace dedicated to variables
    """

    for id_icons in range(len(m.icons)):
        mrs_icons = m.icons[id_icons]
        ICONSNode = ICONS[f"{id_icons}"]

        # adds icons to graphs
        mrsGraph.add((MRSI, MRS.hasIcons, ICONSNode))
        mrsGraph.add((ICONSNode, RDF.type, ERG[mrs_icons.relation]))
        mrsGraph.add((ICONSNode, MRS.leftIcons, VARS[mrs_icons.left])) # should be revisited
        mrsGraph.add((ICONSNode, MRS.rightIcons, VARS[mrs_icons.right])) # should be revisited

        # by now, the ICONSs seems to be grammar-specific
        # and this relation must be defined in ERG as an icons.
        # As we don't have an exhaustive list of the possible icons in ERG (and any other grammar),
        # we'll create on the final graph those icons. This is provisory
        defaultGraph.add((ERG[mrs_icons.relation], RDF.type, RDFS.Class))
        defaultGraph.add((ERG[mrs_icons.relation], RDFS.subClassOf, MRS.Icons))

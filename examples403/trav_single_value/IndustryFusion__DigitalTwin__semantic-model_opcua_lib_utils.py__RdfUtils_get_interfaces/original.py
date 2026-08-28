# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/utils.py
# region: RdfUtils.get_interfaces (lines 781-808, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib.namespace import RDFS, OWL, RDF

def get_interfaces(self, g, node):
    """Get all interfaces with their corresponding typenodes

       Cannot be done with a query since the order matters
    Args:
        g (Graph): Graph which contains the interface node
        node (URIRef): typenode to start scanning

    Returns:
        : [(URIRef type, URIRef node)]: type, node (instance declaration/type), type
    """
    interface_node = next(g.objects(node, self.opcuans['HasInterface']), None)
    if interface_node is None:
        return []

    supertypes = []
    curtype = None
    curnode = interface_node
    curtype = next(g.objects(curnode, self.basens['definesType']), None)
    while curtype != self.opcuans['BaseInterfaceType'] and curtype is not None:
        if curtype == self.opcuans['BaseObjectType']:
            warnmsg = f"Interface added to {node} is not subtype of BaseInterfaceType."
            print_warning('interface_not_subtype_of_interfacetype', warnmsg)
            break
        supertypes.append((curtype, curnode))
        curtype = next(g.objects(curtype, RDFS.subClassOf), None)
        curnode = next(g.subjects(self.basens['definesType'], curtype), None)
    return supertypes

# Context shim (see meta.json): a trimmed copy of `Entity`, from
# semantic-model/opcua/lib/entity.py in IndustryFusion/DigitalTwin@3b40088b88,
# keeping only the constructor and the three methods the region calls
# (add_subclasses, add_subclasses_recursive, serialize, plus get_graph so
# the driver can reach the built graph). Transcribed verbatim from the real
# file -- nothing here is invented logic. Identical for both representations.
from rdflib import Graph, Namespace
from rdflib.namespace import OWL, RDF, RDFS


class Entity:
    def __init__(self, namespace_prefix, basens, opcuans):
        self.e = Graph()
        self.basens = basens
        self.opcuans = opcuans
        self.entity_namespace = Namespace(f'{namespace_prefix}entity/')
        self.e.bind('uaentity', self.entity_namespace)

    def add_subclasses(self, classes):
        self.e += classes

    def add_subclasses_recursive(self, g, type):
        bindings = {'c': type}
        result = g.query("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?subclass ?parent WHERE {
            ?subclass rdfs:subClassOf+ ?c .
            ?subclass rdfs:subClassOf ?parent .
        }""", initBindings=bindings,
                         initNs={'base': self.basens, 'opcua': self.opcuans})
        for row in result:
            self.e.add((row.subclass, RDF.type, OWL.Class))
            self.e.add((row.subclass, RDF.type, OWL.NamedIndividual))
            self.e.add((row.subclass, RDFS.subClassOf, row.parent))

    def serialize(self, destination):
        self.e.serialize(destination)

    def get_graph(self):
        return self.e

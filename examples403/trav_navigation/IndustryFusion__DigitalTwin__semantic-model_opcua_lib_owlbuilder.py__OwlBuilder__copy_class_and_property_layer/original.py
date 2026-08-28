# Extracted from IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/opcua/lib/owlbuilder.py
# region: OwlBuilder._copy_class_and_property_layer (lines 745-801, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL, RDF, RDFS, XSD, split_uri

def _copy_class_and_property_layer(self):
    for s in self.g.subjects(RDF.type, OWL.Class):
        self.out.add((s, RDF.type, OWL.Class))
        for sup in self.g.objects(s, RDFS.subClassOf):
            self.out.add((s, RDFS.subClassOf, sup))
        for abstract in self.g.objects(s, self.basens['isAbstract']):
            self.out.add((s, self.basens['isAbstract'], abstract))

    # Structural reference-type properties (HasComponent, Aggregates,
    # HasChild, HasOrderedComponent, ...) are already explicitly typed
    # owl:ObjectProperty in the source graph.
    for s in self.g.subjects(RDF.type, OWL.ObjectProperty):
        self.out.add((s, RDF.type, OWL.ObjectProperty))
        for sup in self.g.objects(s, RDFS.subPropertyOf):
            self.out.add((s, RDFS.subPropertyOf, sup))

    # The derived semantic-bridge properties (opcua:has<BrowseName>, ~1047 of
    # them) are NOT: Part 5 only ever asserts
    # `p rdfs:subPropertyOf base:SemanticBridgeReferenceType` for them, never
    # `p a owl:ObjectProperty` -- and base:SemanticBridgeReferenceType itself
    # is never declared as a property either, only ever used as an object.
    # Left alone, every owl:onProperty this module generates in a restriction
    # would reference a wholly undeclared entity. That is exactly what made
    # Protege/the OWL API inject synthetic "ErrorN" placeholder classes (one
    # per occurrence) instead of the real property when loading the previous
    # output -- OWL's punning rules require an entity used as a property to
    # actually be declared as one. Materialize the missing declarations here
    # so every property used in a restriction is properly typed.
    semantic_bridge_root = self.basens['SemanticBridgeReferenceType']
    self.out.add((semantic_bridge_root, RDF.type, OWL.ObjectProperty))
    query = """
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?s ?sup WHERE {
        ?s rdfs:subPropertyOf+ ?root .
        ?s rdfs:subPropertyOf ?sup .
    }
    """
    for s, sup in self.g.query(query, initBindings={'root': semantic_bridge_root}):
        self.out.add((s, RDF.type, OWL.ObjectProperty))
        # Each `s` here is one specific has<BrowseName> leaf property (e.g.
        # opcua:hasMotor), minted per (namespace URI, BrowseName) pair by
        # nodesetparser.add_semantic_bridge -- never an intermediate
        # supertype (every one of them is asserted rdfs:subPropertyOf the
        # SemanticBridgeReferenceType root directly, one flat level, see
        # that function). OPC UA's own uniqueness rule (Part 3: no two
        # forward References of a Node may share a BrowseName) means a
        # given owner can only ever have at most one filler for a specific
        # BrowseName's property, so owl:FunctionalProperty here is simply
        # true, not an approximation -- and it's what makes an OPC UA
        # nodeset that (illegally) declares two same-named children under
        # one node a genuine, HermiT-detectable contradiction rather than
        # a silently-accepted no-op. (semantic_bridge_root itself is
        # deliberately NOT made functional two lines up: it is the shared
        # supertype of *all* has<BrowseName> properties, and a real owner
        # legitimately has many differently-named children at once.)
        self.out.add((s, RDF.type, OWL.FunctionalProperty))
        self.out.add((s, RDFS.subPropertyOf, sup))

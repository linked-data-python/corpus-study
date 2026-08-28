# Extracted from linkml/linkml@680595df54 : packages/linkml/src/linkml/generators/owlgen.py
# region: OwlSchemaGenerator._add_disjoint_children (lines 1301-1320, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import DCTERMS, OWL, RDF, XSD, BNode, Graph, Literal, URIRef
from rdflib.collection import Collection
from linkml_runtime.linkml_model.meta import (
    AnonymousClassExpression,
    AnonymousSlotExpression,
    AnonymousTypeExpression,
    ClassDefinition,
    ClassDefinitionName,
    ClassRule,
    Definition,
    EnumDefinition,
    EnumDefinitionName,
    PermissibleValue,
    SchemaDefinitionName,
    SlotDefinition,
    SlotDefinitionName,
    TypeDefinition,
    TypeDefinitionName,
)

def _add_disjoint_children(self, cls: ClassDefinition) -> None:
    """Emit an ``owl:AllDisjointClasses`` axiom for the immediate subclasses of *cls*
    when ``children_are_mutually_disjoint`` is set on the class.

    The axiom is suppressed when fewer than two qualifying children exist.
    """
    if not cls.children_are_mutually_disjoint:
        return
    sv = self.schemaview
    children = sorted(
        [c for c in sv.all_classes(imports=self.mergeimports).values() if c.is_a == cls.name],
        key=lambda c: c.name,
    )
    if len(children) < 2:
        return
    node = BNode()
    self.graph.add((node, RDF.type, OWL.AllDisjointClasses))
    listnode = BNode()
    Collection(self.graph, listnode, [self._class_uri(c.name) for c in children])
    self.graph.add((node, OWL.members, listnode))

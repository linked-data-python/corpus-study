# Extracted from eclipse-esmf/esmf-sdk-py-aspect-model-loader@5ca56eb51c : core/esmf-aspect-meta-model-python/esmf_aspect_meta_model_python/loader/instantiator/property_instantiator.py
# region: PropertyInstantiator._create_property_blank_node (lines 61-99, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib import BNode
from esmf_context import Property, DefaultProperty, SAMM

def _create_property_blank_node(self, element_node: BNode) -> Property:
    """Handle a blank node holding a reference to the property and having additional attributes.

    All attributes are eagerly resolved.

    Args:
        element_node (BNode): The blank RDF node representing the property.
    Returns:
        Property: The created DefaultProperty instance.
    Raises:
        ValueError: If the property node cannot be found.
    """
    property_node = self._aspect_graph.value(element_node, self._samm.get_urn(SAMM.property))
    if not property_node:
        raise ValueError(f"Could not find property for the node {element_node}")

    return DefaultProperty(
        payload_name=self._get_child(element_node, self._samm.get_urn(SAMM.payload_name)),
        characteristic=self._get_child(
            property_node,  # type: ignore
            self._samm.get_urn(SAMM.characteristic),
            required=True,
        ),
        example_value=self._aspect_graph.value(
            property_node, self._samm.get_urn(SAMM.example_value)
        ),
        meta_model_base_attributes=self._get_base_attributes(property_node),
        optional=(element_node, self._samm.get_urn(SAMM.optional), None) in self._aspect_graph,
        not_in_payload=(
            element_node, self._samm.get_urn(SAMM.not_in_payload), None
        ) in self._aspect_graph,
    )

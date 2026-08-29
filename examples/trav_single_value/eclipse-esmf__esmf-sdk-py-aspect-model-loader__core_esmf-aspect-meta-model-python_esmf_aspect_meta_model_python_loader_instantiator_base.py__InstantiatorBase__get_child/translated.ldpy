# Extracted from eclipse-esmf/esmf-sdk-py-aspect-model-loader@5ca56eb51c : core/esmf-aspect-meta-model-python/esmf_aspect_meta_model_python/loader/instantiator_base.py
# region: InstantiatorBase._get_child (lines 109-134, stratum trav_single_value)
# licence of the source repository: see meta.json
import rdflib
from rdflib.term import Node
from esmf_aspect_meta_model_python.loader.rdf_helper import RdfHelper

def _get_child(self, parent_subject: Node, child_predicate, required=False):
    """Searches for a child node of a parent node and returns an instance of it.

    The child can either be a Literal (e.g., a String) or a sub-element (e.g., Characteristic).

    Args:
        parent_subject (Node): Node in the aspect graph of the parent.
        child_predicate: Predicate that points from the parent to the child.
        required (bool, optional): Whether the child is mandatory. Defaults to False.

    Returns:
        Any: An instance of the child if it exists or None if the child does not exist and is not required.

    Raises:
        ValueError: If the child is required but does not exist.
    """
    child_subject = self._aspect_graph.value(subject=parent_subject, predicate=child_predicate)

    if child_subject is None and required:
        raise ValueError(f"Child {child_predicate} is required for element {RdfHelper.to_python(parent_subject)}")
    elif child_subject is None:  # not required
        return None
    elif isinstance(child_subject, rdflib.Literal):
        return RdfHelper.to_python(child_subject)
    else:
        return self._model_element_factory.create_element(child_subject, parent_subject, attr_name=child_predicate)

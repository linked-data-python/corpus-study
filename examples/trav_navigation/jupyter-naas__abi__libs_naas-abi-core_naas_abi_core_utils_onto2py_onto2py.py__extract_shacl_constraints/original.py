# Extracted from jupyter-naas/abi@3fb7f5304d : libs/naas-abi-core/naas_abi_core/utils/onto2py/onto2py.py
# region: extract_shacl_constraints (lines 1697-1714, stratum trav_navigation)
# licence of the source repository: see meta.json
import rdflib
from context_shim import ClassInfo, PropertyInfo, process_property_shape  # context shim -- see meta.json

def extract_shacl_constraints(
    g: rdflib.Graph,
    classes: dict[str, ClassInfo],
    properties: dict[str, PropertyInfo],
    SHACL,
):
    """Extract SHACL constraints and apply them to properties"""

    # Find SHACL shapes
    for shape in g.subjects(rdflib.RDF.type, SHACL.NodeShape):
        # Get target class
        for target_class in g.objects(shape, SHACL.targetClass):
            if str(target_class) in classes:
                # Process property shapes
                for prop_shape in g.objects(shape, SHACL.property):
                    process_property_shape(
                        g, prop_shape, classes[str(target_class)], properties, SHACL
                    )

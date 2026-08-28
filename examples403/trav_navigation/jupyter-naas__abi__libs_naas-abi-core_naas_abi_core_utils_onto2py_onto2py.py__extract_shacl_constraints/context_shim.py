# Context shim (see meta.json): subset of
# libs/naas-abi-core/naas_abi_core/utils/onto2py/onto2py.py from
# jupyter-naas/abi@3fb7f5304d311461a2b5716f8a2144f377fd3b48, so the region
# executes outside the package (the file is 2900+ lines; only the three
# names `extract_shacl_constraints` calls but does not define itself are
# reproduced here, unmodified). Identical bindings for both representations.

from dataclasses import dataclass, field


@dataclass
class PropertyInfo:
    """Information about a property (data or object property)"""

    name: str
    property_type: str  # 'data' or 'object'
    range_classes: dict[str, int | None] = field(
        default_factory=dict
    )  # Dict mapping class name to cardinality (None = not specified, > 1 = list, 1 or 0 = single)
    datatype: str | None = None
    required: bool = False
    description: str | None = None  # skos:definition
    default_value: str | None = (
        None  # Default value expression (e.g., "datetime.now()")
    )


@dataclass
class ClassInfo:
    """Information about an RDF class"""

    name: str
    uri: str
    parent_classes: list[str]
    properties: list[PropertyInfo]
    description: str | None = None
    property_uris: dict[str, str] = field(
        default_factory=dict
    )  # Maps property name to URI
    label: str | None = None  # rdfs:label
    external_module: str | None = None


def process_property_shape(
    g,
    prop_shape,
    class_info: ClassInfo,
    properties: dict[str, PropertyInfo],
    SHACL,
):
    """Process a SHACL property shape"""

    # Get the property path
    for path in g.objects(prop_shape, SHACL.path):
        if str(path) in properties:
            prop_info = properties[str(path)]

            # Check cardinality constraints
            for min_count in g.objects(prop_shape, SHACL.minCount):
                if int(str(min_count)) > 0:
                    prop_info.required = True

            # Update cardinality for all range classes if maxCount is specified
            max_count_val = None
            for max_count in g.objects(prop_shape, SHACL.maxCount):
                max_count_val = int(str(max_count))
                break

            if max_count_val is not None:
                # Update all range classes with the cardinality
                for cls_name in prop_info.range_classes:
                    if max_count_val > 1:
                        prop_info.range_classes[cls_name] = max_count_val
                    else:
                        prop_info.range_classes[cls_name] = 1

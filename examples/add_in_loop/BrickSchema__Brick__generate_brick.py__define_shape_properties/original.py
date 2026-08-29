# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: define_shape_properties (lines 527-615, stratum add_in_loop)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, BNode, URIRef
from rdflib.collection import Collection
from bricksrc.namespaces import (
    BRICK,
    BSH,
    REC,
    RDF,
    OWL,
    RDFS,
    TAG,
    SOSA,
    SKOS,
    QUDT,
    VCARD,
    SH,
    REF,
)
G = brickschema.Graph()
A = RDF.type

def define_shape_properties(definitions, graph=G):
    """
    Defines the NodeShapes that govern what the values of
    EntityProperty relationships should look like. The important
    keys are:
    - values: defines the set of possible values of this property as an enumeration
    - units: verifies that the units of the value are one of the given enumeration.
    - unitsFromQuantity: verifies that the units of the value are compatible with the units
                for the given Brick quantity
    - datatype: specifies the expected kind of data type of prop:value
    - properties: defines other epected properties of the Shape. These properties can have
                'datatype' or 'values', in addition to other standard properties like
                SKOS.definition

    Some other usage notes:
    - 'units' and 'datatype' should be used together
    - 'values' should not be used with units or datatype
    """
    for shape_name, defn in definitions.items():
        graph.add((shape_name, A, SH.NodeShape))
        graph.add((shape_name, RDFS.subClassOf, BSH.ValueShape))

        needs_value_properties = ["values", "units", "unitsFromQuantity", "datatype"]
        brick_value_shape = BNode()
        if any(k in defn for k in needs_value_properties):
            graph.add((shape_name, SH.property, brick_value_shape))
            graph.add((brick_value_shape, A, SH.PropertyShape))
            graph.add((brick_value_shape, SH.path, BRICK.value))
            graph.add((brick_value_shape, SH.minCount, Literal(1)))
            graph.add((brick_value_shape, SH.maxCount, Literal(1)))

        v = BNode()
        # prop:value PropertyShape
        if "values" in defn:
            enumeration = BNode()
            graph.add((shape_name, SH.property, brick_value_shape))
            graph.add((brick_value_shape, A, SH.PropertyShape))
            graph.add((brick_value_shape, SH.path, BRICK.value))
            graph.add((brick_value_shape, SH["in"], enumeration))
            graph.add((brick_value_shape, SH.minCount, Literal(1)))
            vals = defn.pop("values")
            Collection(graph, enumeration, map(Literal, vals))
        if "units" in defn:
            v = BNode()
            enumeration = BNode()
            graph.add((shape_name, SH.property, v))
            graph.add((v, A, SH.PropertyShape))
            graph.add((v, SH.path, BRICK.hasUnit))
            graph.add((v, SH["in"], enumeration))
            graph.add((v, SH.minCount, Literal(1)))
            graph.add((v, SH.maxCount, Literal(1)))
            Collection(graph, enumeration, defn.pop("units"))
        if "unitsFromQuantity" in defn:
            v = BNode()
            enumeration = BNode()
            graph.add((shape_name, SH.property, v))
            graph.add((v, A, SH.PropertyShape))
            graph.add((v, SH.path, BRICK.hasUnit))
            graph.add((v, SH["in"], enumeration))
            graph.add((v, SH.minCount, Literal(1)))
            graph.add((v, SH.maxCount, Literal(1)))
            units = units_for_quantity(defn.pop("unitsFromQuantity"))
            assert len(units) > 0, f"Quantity shape {shape_name} has no units"
            Collection(graph, enumeration, units)
        if "properties" in defn:
            prop_defns = defn.pop("properties")
            define_shape_property_property(shape_name, prop_defns, graph=graph)
        elif "datatype" in defn:
            graph.add((shape_name, SH.property, brick_value_shape))
            graph.add((brick_value_shape, A, SH.PropertyShape))
            graph.add((brick_value_shape, SH.path, BRICK.value))
            dtype = defn.pop("datatype")
            if dtype == BSH.NumericValue:
                graph.add((brick_value_shape, SH["or"], BSH.NumericValue))
            else:
                graph.add((brick_value_shape, SH.datatype, dtype))
            graph.add((brick_value_shape, SH.minCount, Literal(1)))
            if "range" in defn:
                for prop_name, prop_value in defn.pop("range").items():
                    if prop_name not in [
                        "minExclusive",
                        "minInclusive",
                        "maxExclusive",
                        "maxInclusive",
                    ]:
                        raise Exception(
                            f"brick:value property {prop_name} not valid"  # noqa
                        )
                    graph.add((brick_value_shape, SH[prop_name], Literal(prop_value)))

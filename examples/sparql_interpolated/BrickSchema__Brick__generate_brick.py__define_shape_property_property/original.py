# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: define_shape_property_property (lines 463-524, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, BNode, URIRef
from rdflib.collection import Collection
from context_shim import (
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
    brickschema,
    add_relationships,
)
G = brickschema.Graph()
A = RDF.type

def define_shape_property_property(shape_name, definitions, graph=G):
    if "or" in definitions:
        or_list = []
        for or_node_defn in definitions.pop("or"):
            or_node_shape = BNode()
            or_list.append(or_node_shape)
            define_shape_property_property(or_node_shape, or_node_defn, graph=graph)
        or_list_name = BNode()
        graph.add((shape_name, SH["or"], or_list_name))
        Collection(graph, or_list_name, or_list)
    for prop_name, prop_defn in definitions.items():
        # check if there is already a property shape for this.
        # Only do this is if (a) the property is optional for this shape, and
        # (b) there are no further requirements; the existing property shapes
        # don't have any min/max counts or additional requirements
        if prop_defn.get("optional", False) and len(prop_defn.keys()) == 1:
            prop_exists = list(
                graph.query(
                    f"""SELECT ?x {{ ?p sh:property ?p .
                        ?p sh:path {prop_name.n3()} .
                        FILTER NOT EXISTS {{ ?p sh:minCount ?mc }}
                        FILTER NOT EXISTS {{ ?p sh:maxCount ?mc }}
                    }}"""  # noqa
                )
            )
            if len(prop_exists) > 0:
                graph.add((shape_name, SH.property, prop_exists[0][0]))
                continue  # continue to next property

        ps = BNode()
        graph.add((shape_name, SH.property, ps))
        graph.add((ps, A, SH.PropertyShape))
        graph.add((ps, SH.path, prop_name))
        if "import_from" in prop_defn:
            fname = prop_defn.pop("import_from")
            tmpG = Graph()
            tmpG.parse(fname)
            res = tmpG.query(f"SELECT ?p ?o WHERE {{ <{prop_name}> ?p ?o }}")  # noqa
            for p, o in res:
                graph.add((prop_name, p, o))
        if "optional" in prop_defn:
            if not prop_defn.pop("optional"):
                graph.add((ps, SH.minCount, Literal(1)))
        else:
            graph.add((ps, SH.minCount, Literal(1)))

        if "datatype" in prop_defn:
            dtype = prop_defn.pop("datatype")
            graph.add((prop_name, A, OWL.DatatypeProperty))
            if dtype == BSH.NumericValue:
                graph.add((ps, SH["or"], BSH.NumericValue))
            else:
                graph.add((ps, SH.datatype, dtype))
        elif "values" in prop_defn:
            enumeration = BNode()
            graph.add((ps, SH["in"], enumeration))
            graph.add((ps, SH.minCount, Literal(1)))
            Collection(graph, enumeration, map(Literal, prop_defn.pop("values")))
            graph.add((prop_name, A, OWL.DatatypeProperty))
        else:
            graph.add((prop_name, A, OWL.ObjectProperty))
        add_relationships(ps, prop_defn, graph=graph)

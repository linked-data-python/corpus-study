# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: define_relationships (lines 618-684, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import BNode, URIRef
from rdflib.collection import Collection
import brick_context as brickschema
from brick_context import BRICK, BSH, RDF, RDFS, SH, add_relationships
G = brickschema.Graph()
A = RDF.type

def define_relationships(definitions, superprop=None, graph=G):
    """
    Define BRICK relationships
    """
    if len(definitions) == 0:
        return

    for prop, propdefn in definitions.items():
        if not isinstance(prop, URIRef):
            prop = BRICK[prop]
        if superprop is not None:
            graph.add((prop, RDFS.subPropertyOf, superprop))

        if prop.startswith(BRICK):
            graph.add((prop, A, BRICK.Relationship))

        # define property types
        prop_types = propdefn.get(A, [])
        assert isinstance(prop_types, list)
        graph += [(prop, A, prop_type) for prop_type in prop_types]

        # define any subproperties
        subproperties_def = propdefn.get("subproperties", {})
        assert isinstance(subproperties_def, dict)
        define_relationships(subproperties_def, prop, graph=graph)

        # generate a SHACL Property Shape for this relationship if it is a Brick property
        if prop.startswith(BRICK):
            propshape = BSH[f"{prop[len(BRICK) :]}Shape"]
            graph += [(propshape, A, SH.PropertyShape), (propshape, SH.path, prop)]
        range_defn = propdefn.pop("range", None)
        if isinstance(range_defn, (tuple, list)):
            enumeration = BNode()
            graph.add((propshape, SH["or"], enumeration))
            constraints = []
            for cls in range_defn:
                constraint = BNode()
                graph.add((constraint, SH["class"], cls))
                constraints.append(constraint)
            Collection(graph, enumeration, constraints)
        elif range_defn is not None:
            graph.add((propshape, SH["class"], range_defn))

        if "datatype" in propdefn:
            dtype_defn = propdefn.pop("datatype")
            graph.add((propshape, SH["or"] if dtype_defn == BSH.NumericValue else SH.datatype, dtype_defn))

        if "domain" in propdefn:
            # associate the PropertyShape with all possible subject classes
            domains = propdefn.pop("domain")
            if not isinstance(domains, list):
                domains = [domains]
            graph += [(domain, SH.property, propshape) for domain in domains]

        # define other properties of the Brick property
        add_relationships(
            prop, {k: v for k, v in propdefn.items() if k not in ["subproperties", A]}, graph=graph
        )

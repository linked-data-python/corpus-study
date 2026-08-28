# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: define_relationships (lines 618-684, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, BNode, URIRef
from rdflib.collection import Collection
import brick_context as brickschema
from brick_context import (
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
    add_relationships,
)
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
        for prop_type in prop_types:
            graph.add((prop, A, prop_type))

        # define any subproperties
        subproperties_def = propdefn.get("subproperties", {})
        assert isinstance(subproperties_def, dict)
        define_relationships(subproperties_def, prop, graph=graph)

        # generate a SHACL Property Shape for this relationship if it is a Brick property
        if prop.startswith(BRICK):
            propshape = BSH[f"{prop[len(BRICK) :]}Shape"]
            graph.add((propshape, A, SH.PropertyShape))
            graph.add((propshape, SH.path, prop))
        if "range" in propdefn.keys():
            range_defn = propdefn.pop("range")
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

        if "datatype" in propdefn.keys():
            dtype_defn = propdefn.pop("datatype")
            if dtype_defn == BSH.NumericValue:
                graph.add((propshape, SH["or"], BSH.NumericValue))
            else:
                graph.add((propshape, SH.datatype, dtype_defn))

        if "domain" in propdefn.keys():
            # associate the PropertyShape with all possible subject classes
            domains = propdefn.pop("domain")
            if not isinstance(domains, list):
                domains = [domains]
            for domain in domains:
                graph.add((domain, SH.property, propshape))

        # define other properties of the Brick property
        expected_properties = ["subproperties", A]
        other_properties = [
            prop for prop in propdefn.keys() if prop not in expected_properties
        ]
        add_relationships(prop, {k: propdefn[k] for k in other_properties}, graph=graph)

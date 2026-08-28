# Extracted from BrickSchema/Brick@c12949f236 : generate_brick.py
# region: define_classes (lines 294-374, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import logging
from rdflib import Graph, Literal, BNode, URIRef
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

def define_classes(definitions, parent, pun_classes=False, graph=G):
    """
    Generates triples for the hierarchy given by 'definitions', rooted
    at the class given by 'parent'
    - class hierarchy ('subclasses')
    - tag mappings
    - substance + quantity modeling

    If pun_classes is True, then create punned instances of the classes
    """
    for classname, defn in definitions.items():
        classname = BRICK[classname] if not isinstance(classname, URIRef) else classname
        # class is a owl:Class
        graph.add((classname, A, OWL.Class))
        graph.add((classname, A, SH.NodeShape))
        # subclass of parent
        graph.add((classname, RDFS.subClassOf, parent))

        if pun_classes:
            graph.add((classname, A, classname))

        # define mapping to tags if it exists
        # "tags" property is a list of URIs naming Tags
        taglist = defn.get("tags", [])
        assert isinstance(taglist, list)
        if len(taglist) == 0:
            logging.warning(f"Property 'tags' not defined for {classname}")
        add_tags(classname, taglist, graph=graph)

        # define class structure
        # this is a nested dictionary
        subclassdef = defn.get("subclasses", {})
        assert isinstance(subclassdef, dict)
        define_classes(subclassdef, classname, graph=graph)

        # handle 'parents' subclasses (links outside of tree-based hierarchy)
        parents = defn.get("parents", [])
        assert isinstance(parents, list)
        for _parent in parents:
            graph.add((classname, RDFS.subClassOf, _parent))

        # add SHACL constraints to the class
        constraints = defn.get("constraints", {})
        assert isinstance(constraints, dict)
        define_constraints(constraints, classname, graph=graph)

        aliases = defn.get("aliases", [])
        assert isinstance(aliases, list)
        for alias in aliases:
            graph.add((classname, OWL.equivalentClass, alias))
            graph.add((alias, A, OWL.Class))
            graph.add((alias, A, SH.NodeShape))
            graph.add((alias, OWL.equivalentClass, classname))
            # find parent class of what the alias is equivalent to, add the RDFS subClassOf properties
            parent_classes = list(
                graph.objects(subject=classname, predicate=RDFS.subClassOf)
            )
            for pc in parent_classes:
                graph.add((alias, RDFS.subClassOf, pc))
            graph.add((alias, BRICK.aliasOf, classname))

        # all other key-value pairs in the definition are
        # property-object pairs
        expected_properties = [
            "parents",
            "tags",
            "substances",
            "subclasses",
            "constraints",
            "aliases",
        ]
        other_properties = [
            prop for prop in defn.keys() if prop not in expected_properties
        ]
        for propname in other_properties:
            propval = defn[propname]
            if isinstance(propval, list):
                for pv in propval:
                    graph.add((classname, propname, pv))
            else:
                graph.add((classname, propname, propval))

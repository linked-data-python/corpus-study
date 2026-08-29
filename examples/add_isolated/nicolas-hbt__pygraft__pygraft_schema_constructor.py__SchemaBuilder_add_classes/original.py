# Extracted from nicolas-hbt/pygraft@12933c0769 : pygraft/schema_constructor.py
# region: SchemaBuilder.add_classes (lines 125-156, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef
from tqdm.auto import tqdm

def add_classes(self):
    """
    Adds classes to the graph based on the given class info.

    Args:
        self (object): The instance of the SchemaBuilder.

    Returns:
        None
    """
    classes = self.class_info["classes"]
    class2superclass = self.class_info["direct_class2superclass"]
    class2disjoints = self.class_info["class2disjoints"]

    for c in tqdm(classes, desc="Writing classes", unit="classes", colour="red"):
        class_URI = URIRef(self.schema + str(c))

        self.graph.add((class_URI, RDF.type, OWL.Class))

        if c in class2superclass:
            sp = class2superclass[c]

            if sp == "owl:Thing":
                self.graph.add((class_URI, RDFS.subClassOf, OWL.Thing))
            else:
                self.graph.add((class_URI, RDFS.subClassOf, URIRef(self.schema + str(sp))))

        if c in class2disjoints:
            for c2 in class2disjoints[c]:
                self.graph.add((class_URI, OWL.disjointWith, URIRef(self.schema + str(c2))))

    print("\n")

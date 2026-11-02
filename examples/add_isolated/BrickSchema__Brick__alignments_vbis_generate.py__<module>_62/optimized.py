# Extracted from BrickSchema/Brick@c12949f236 : alignments/vbis/generate.py
# region: <module> (lines 62-125, stratum add_isolated)
# licence of the source repository: see meta.json
import csv
from rdflib import Graph, Namespace, Literal, BNode
from rdflib import RDF, RDFS, XSD, OWL
from rdflib.collection import Collection
from vbis_context import get_brick_class, get_vbis_tags, rewrite_vbis_pattern
graph = Graph()
BRICK = Namespace("https://brickschema.org/schema/Brick#")
SH = Namespace("http://www.w3.org/ns/shacl#")
VBIS = Namespace("https://brickschema.org/schema/Brick/alignments/vbis#")
finished_brick_classes = set()

with open("vbis-brick-v5.csv") as f:
    for d in csv.DictReader(f):
        bc = get_brick_class(d)
        if bc is None or bc in finished_brick_classes:
            continue
        finished_brick_classes.add(bc)
        tagsOrPatterns = get_vbis_tags(d)
        if not tagsOrPatterns:
            continue
        print(f"Defining shapes for {bc}")
        # create a shape for each set of tags
        node_shape = VBIS[f"{bc}Shape"]
        graph += [(node_shape, RDF.type, SH.NodeShape), (node_shape, SH.targetClass, BRICK[bc])]

        # patterns is the list of patterns that match this Brick class
        patterns = []
        # vbtags is the list of fully qualified VB tags that match this Brick class
        vbtags = []
        # loop through all of the tags and/or patterns we get and sort them into
        # the above two lsits
        for vb in tagsOrPatterns:
            isPattern, patOrValue = rewrite_vbis_pattern(vb)
            (patterns if isPattern else vbtags).append(patOrValue)
        print(f"{len(patterns)} patterns; {len(vbtags)} full tags")

        # handle patterns; this is either a SH:pattern directly (if there is one)
        # or a SH:or of a set of patterns (if there is > 1)
        if len(patterns) > 1:
            shapeList = BNode()
            graph.add((node_shape, SH["or"], shapeList))
            patternList = []
            for vbtag in patterns:
                pattern = BNode()
                patternList.append(pattern)
                graph += [(pattern, RDF.type, SH.PropertyShape),
                          (pattern, SH.path, VBIS.hasVBISTag),
                          (pattern, SH.pattern, Literal(vbtag))]
            Collection(graph, shapeList, patternList)
        else:
            shape = BNode()
            graph += [(node_shape, SH.property, shape),
                      (shape, RDF.type, SH.PropertyShape),
                      (shape, SH.path, VBIS.hasVBISTag)]
            if patterns:
                graph.add((shape, SH.pattern, Literal(patterns[0])))
            # handle fully qualified tags. If there is one, then it is a mandatory
            # value. If there are multiple, then we must have one of them as a value
            elif len(vbtags) == 1:
                graph.add((shape, SH.hasValue, Literal(vbtags[0])))
            else:
                valueList = BNode()
                graph.add((shape, SH["in"], valueList))
                Collection(graph, valueList, [Literal(x) for x in vbtags])

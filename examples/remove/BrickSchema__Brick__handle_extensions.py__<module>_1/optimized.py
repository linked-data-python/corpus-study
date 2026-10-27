# Extracted from BrickSchema/Brick@c12949f236 : handle_extensions.py
# region: <module> (lines 1-37, stratum remove)
# licence of the source repository: see meta.json
import glob
import rdflib

# read the base Brick ontology
from rdflib import Graph, OWL, RDF, SH, URIRef
brick_graph = Graph()
brick_graph.parse("Brick.ttl", format="ttl")
BRICK = URIRef("https://brickschema.org/schema/1.5/Brick")

# add extension files to Brick graph
for filename in glob.glob("extensions/*.ttl"):
    brick_graph.parse(filename)

# remove duplicate ontology definitions and
# move prefixes onto Brick ontology definition
for pfx in brick_graph.objects(predicate=SH.declare):
    brick_graph.remove((None, SH.declare, pfx))
    brick_graph.add((BRICK, SH.declare, pfx))

# reassign where rules find their prefixees
for rule in brick_graph.subjects(predicate=SH.prefixes):
    brick_graph.set((rule, SH.prefixes, BRICK))

# remove ontology declarations
for ontology in brick_graph.subjects(predicate=RDF.type, object=OWL.Ontology):
    if ontology != BRICK:
        brick_graph.remove((ontology, RDF.type, OWL.Ontology))
        brick_graph.remove((ontology, OWL.imports, None))
        brick_graph.remove((ontology, OWL.versionInfo, None))

# serialize Brick with all extensions added
with open("Brick+extensions.ttl", "w", encoding="utf-8") as fp:
    fp.write(brick_graph.serialize(format="turtle").rstrip() + "\n")

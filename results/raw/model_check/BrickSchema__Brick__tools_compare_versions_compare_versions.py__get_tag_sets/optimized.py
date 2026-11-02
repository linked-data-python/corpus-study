# Extracted from BrickSchema/Brick@c12949f236 : tools/compare_versions/compare_versions.py
# region: get_tag_sets (lines 95-107, stratum sparql_interpolated)
# licence of the source repository: see meta.json
from rdflib import Graph
g = Graph()

# `graph=g` restores the binding to the module-level `g` the original
# closes over silently, as an annotated parameter (see AGENT_BATCH.md,
# "163 regions... restore the binding"), so the region can be driven with a
# fixture graph instead of the always-empty module `g`. Both representations
# get the identical change.
def get_tag_sets(root, graph=g):
    classes = (row[0].split("#")[-1] for row in graph.query(
        f"select ?class where {{ ?class rdfs:subClassOf+ <{root}>. }}"))
    tag_sets = {klass: set(klass.split("_")) for klass in classes}  # Tags inside the class name.
    print(root, len(tag_sets))
    return tag_sets

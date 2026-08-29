# Extracted from BrickSchema/Brick@c12949f236 : tools/compare_versions/compare_versions.py
# region: get_tag_sets (lines 95-107, stratum sparql_interpolated)
# licence of the source repository: see meta.json
g = Graph()

def get_tag_sets(root):
    tag_sets = {}
    qstr_allclasses = """
    select ?class where {{
      ?class rdfs:subClassOf+ <{0}>.
    }}
    """
    for row in g.query(qstr_allclasses.format(root)):
        klass = row[0].split("#")[-1]
        tag_set = klass.split("_")  # Tags inside the class name.
        tag_sets[klass] = set(tag_set)
    print(root, len(tag_sets))
    return tag_sets

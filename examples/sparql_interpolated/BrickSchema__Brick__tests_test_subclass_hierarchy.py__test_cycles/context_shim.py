# Context shim (see meta.json): the `minify` test helper from
# tests/test_subclass_hierarchy.py in BrickSchema/Brick@c12949f236, needed
# because the extraction only captured the region's own lines. Identical
# for both representations -- it is plain Python, unrelated to any island.
def minify(node):
    return node.split("#")[-1]

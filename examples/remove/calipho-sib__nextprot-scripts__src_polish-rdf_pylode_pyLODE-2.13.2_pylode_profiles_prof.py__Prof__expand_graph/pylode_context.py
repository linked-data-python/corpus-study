# Context shim (see meta.json): the part of Prof that the region touches,
# from calipho-sib/nextprot-scripts@f03504ce5e
# src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/prof.py, so the region
# (a method body lifted out of its class) executes outside pyLODE 2.13.2.
# Identical for both representations.  Prof.__init__ parses the profile into
# `self.G`; here the caller hands the graph in.
class Prof:
    def __init__(self, G):
        self.G = G

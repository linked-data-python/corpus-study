# Context shim (see meta.json): the module-level name the region calls,
# from rdflib/extras/infixowl.py at MKLab-ITI/prophet@eee2ab51de.  The
# module itself cannot be imported here (its first statement is
# `from rdflib import py3compat`, a helper dropped from rdflib long ago),
# and CastClass pulls in Restriction/BooleanClass/Class — ~1500 lines.
#
# Reduction, documented: CastClass(c, g) is replaced by the plain-Class
# branch of what it returns, i.e. an object whose .serialize(target) copies
# every triple of `c` from `g` into `target` — infixowl.Class.serialize,
# lines 927-930, with an empty _serialize().  The fixtures only use plain
# class members, so this is the branch the real CastClass would take.
# Used IDENTICALLY by original.py and translated.ldpy.


class _PlainClass:
    def __init__(self, identifier, graph):
        self.identifier = identifier
        self.graph = graph

    def serialize(self, graph):
        # infixowl.Class.serialize, lines 927-930
        for fact in self.graph.triples((self.identifier, None, None)):
            graph.add(fact)


def CastClass(c, graph=None):
    return _PlainClass(c, graph)

# Context shim (see meta.json): infixowl's Class, which AllClasses yields, is
# defined further down the same module (MKLab-ITI/prophet@eee2ab51de,
# rdflib/extras/infixowl.py:888) and drags in AnnotatableTerms/Individual and
# a module-level factory graph.  The region only wraps the subject it found,
# so this inert stand-in keeps the identifier (and value equality, so the two
# representations' results can be compared).  Identical for both sides.


class Class:
    def __init__(self, identifier):
        self.identifier = identifier

    def __eq__(self, other):
        return isinstance(other, Class) and self.identifier == other.identifier

    def __hash__(self):
        return hash((Class, self.identifier))

    def __repr__(self):
        return 'Class(%r)' % (self.identifier,)

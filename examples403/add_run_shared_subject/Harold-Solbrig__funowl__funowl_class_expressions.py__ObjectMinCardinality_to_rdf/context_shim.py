# Context shim (see meta.json): minimal stand-ins for the funowl class
# hierarchy ObjectMinCardinality.to_rdf depends on
# (funowl/class_expressions.py), from
# Harold-Solbrig/funowl@69e1cbe2f615b4d64712ad9d5ab8f4d24988c006.
#
# ExprTerm is a minimal stand-in for the real ObjectPropertyExpression /
# ClassExpression / cardinality-value wrappers behind
# self.objectPropertyExpression, self.classExpression and self.min_:
# to_rdf only ever calls their .to_rdf(g), so that is all this shim
# reproduces -- the same reduction as the sibling region Annotatable_TANN
# in this lot's stratum.
from rdflib import Graph


class ExprTerm:
    """Stand-in for ObjectPropertyExpression / ClassExpression / a
    cardinality-value wrapper: to_rdf only ever calls .to_rdf(g) on
    self.objectPropertyExpression, self.classExpression and self.min_."""

    def __init__(self, rdf_term):
        self._rdf_term = rdf_term

    def to_rdf(self, g: Graph):
        return self._rdf_term


class ObjectMinCardinality:
    """Minimal stand-in for funowl's ObjectMinCardinality
    (funowl/class_expressions.py): to_rdf only ever reads
    self.objectPropertyExpression, self.classExpression and self.min_ off
    `self`."""

    def __init__(self, ope_rdf, min_rdf, class_rdf=None):
        self.objectPropertyExpression = ExprTerm(ope_rdf)
        self.min_ = ExprTerm(min_rdf)
        self.classExpression = ExprTerm(class_rdf) if class_rdf is not None else None

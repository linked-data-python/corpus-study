# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/extras/infixowl.py
# region: BooleanClassExtentHelper.__call__._getExtent (lines 1492-1494, stratum trav_one_step)
# licence of the source repository: see meta.json
from rdflib.namespace import OWL
from context_shim import BooleanClass, BooleanClassExtentHelper, Individual

# `_getExtent` closes over `self`, the BooleanClassExtentHelper(operator)
# instance that __call__ provides in the source (lines 1490-1496); the
# pipeline's context window captured only the inner function, not its
# enclosing method, so the binding is restored here. BooleanClass.getUnions
# is built exactly this way, with operator=OWL.unionOf (lines 1619-1623).
self = BooleanClassExtentHelper(OWL.unionOf)

def _getExtent():  # noqa: N802
    for c in Individual.factoryGraph.subjects(self.operator):
        yield BooleanClass(c, operator=self.operator)

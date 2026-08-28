# Extracted from LexMalta/recipes@b861b7ccea : recipe-importer/rdflib/extras/infixowl.py
# region: BooleanClassExtentHelper.__call__._getExtent (lines 1492-1494, stratum trav_one_step)
# licence of the source repository: see meta.json
def _getExtent():  # noqa: N802
    for c in Individual.factoryGraph.subjects(self.operator):
        yield BooleanClass(c, operator=self.operator)

# Context shim (see meta.json): Individual, BooleanClass and
# BooleanClassExtentHelper, the classes `_getExtent`
# (BooleanClassExtentHelper.__call__, lines 1490-1496 of the source file)
# closes over and calls. Imported from the installed rdflib.extras.infixowl
# (rdflib 7.2.1, pinned for this study -- see ldpy/README) rather than
# transcribed: LexMalta/recipes@b861b7ccea vendors, at this region's own path
# (recipe-importer/rdflib/extras/infixowl.py), a near-verbatim copy of this
# same upstream module -- diffed against the installed one, the differences
# around Individual/BooleanClass are cosmetic (docstring wording, the
# `<<...>>` vs `@` infix spelling); the traversal this region exercises
# (Individual.factoryGraph.subjects(operator), BooleanClass.__init__ reading
# the rdf:List at (identifier, operator, ?)) is identical in both.
# Reproducing several hundred lines of OWL class-algebra machinery by hand
# here would not be "minimal", and the behaviour is not project-specific --
# it is rdflib's own extras module, not LexMalta/recipes application logic.
# Identical bindings for both representations.
from rdflib.extras.infixowl import (  # noqa: F401
    BooleanClass,
    BooleanClassExtentHelper,
    Individual,
)

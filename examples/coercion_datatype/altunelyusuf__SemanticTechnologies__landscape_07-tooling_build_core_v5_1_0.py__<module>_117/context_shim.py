# Context shim (see meta.json): BASEDIR points to a minimal on-disk stand-in
# for the ontology tree loaded by landscape/07-tooling/build_core_*.py in
# altunelyusuf/SemanticTechnologies@bad0fa7c46, so the region executes
# outside the package. S(*refs) reproduces the source-citation helper used
# to build the dcterms:source annotation. Identical bindings for both
# representations.
import os

BASEDIR = os.path.join(os.path.dirname(__file__), "fixtures")


def S(*refs):
    return " ".join(refs)

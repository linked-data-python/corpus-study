# Context shim (see meta.json): `_label`, from factsheet/helper.py in
# OpenEnergyPlatform/oeplatform@ff28ef6390, transcribed verbatim so the
# region executes outside the package (importing `factsheet` pulls in
# Django/Flask-side app config not available in the study venv).
# `_division_members`'s sort key calls it; identical for both representations.
#
# The real file imports RDFS from factsheet.oekg.namespaces, which is a
# plain `Namespace("http://www.w3.org/2000/01/rdf-schema#")` -- the same
# IRI as rdflib's own RDFS namespace, used here instead.
from rdflib import Graph, URIRef
from rdflib.namespace import RDFS


def _label(g: Graph, node: URIRef):
    lab = g.value(node, RDFS.label)
    return str(lab) if lab else None

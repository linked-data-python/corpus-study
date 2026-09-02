# Context shim (see meta.json): the four Namespace objects from
# yurtle_rdflib/namespaces.py, Congruentsys/yurtle-rdflib@8bbb378f5a18, so
# the region executes outside its package (the real `.namespaces` relative
# import does not resolve for a single extracted file). Identical bindings
# for both representations; transcribed verbatim.
from rdflib import Namespace

YURTLE = Namespace("https://yurtle.dev/schema/")
PM = Namespace("https://yurtle.dev/pm/")
BEING = Namespace("https://yurtle.dev/being/")
PROVENANCE = Namespace("https://yurtle.dev/provenance/")

__namespaces__ = {"yurtle": YURTLE, "pm": PM, "being": BEING, "provenance": PROVENANCE}

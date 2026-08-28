# Context shim (see meta.json): the three bindings of
# landscape/07-tooling/build_core_v4_4_0.py that the extracted context lines do
# not carry -- the rdflib import (line 8), BASEDIR (line 11) and SRNS (line 96,
# the line right after the parse) -- with the upstream IRI.  Upstream BASEDIR is
# "/home/claude/semtech-landscape" and 01-research/semtech_research_v4_3_0.ttl
# is a build artefact the repository does not contain; here BASEDIR is this
# example directory and 01-research/ holds a fixture standing in for it.
# Identical bindings for both representations.
import os

from rdflib import Graph, Namespace, URIRef, Literal

BASEDIR = os.path.dirname(os.path.abspath(__file__))
SRNS = Namespace("http://example.org/semtech/research#")

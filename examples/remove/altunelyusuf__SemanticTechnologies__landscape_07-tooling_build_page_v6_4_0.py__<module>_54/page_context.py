# Context shim (see meta.json): the two lines of
# landscape/07-tooling/build_page_v6_4_0.py that the extracted context does not
# carry -- the rdflib import of line 9 and HERE of line 12 -- plus the location
# of the input graph.  Upstream HERE is "/home/claude/semtech-landscape" and
# 04-page/semtech_page_abox_v6_3_0.ttl is a build artefact that the repository
# does not contain; here HERE is this example directory and 04-page/ holds a
# fixture standing in for that artefact.  Identical bindings for both
# representations.
import os

from rdflib import Graph, Namespace, URIRef, Literal

HERE = os.path.dirname(os.path.abspath(__file__))

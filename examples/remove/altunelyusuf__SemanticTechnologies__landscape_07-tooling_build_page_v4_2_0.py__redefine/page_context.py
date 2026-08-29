# Context shim (see meta.json): the two bindings of
# landscape/07-tooling/build_page_v4_2_0.py that the extracted context lines do
# not carry -- HERE (line 12) and SP (line 29, the page namespace the callers of
# redefine use) -- with the upstream IRI.  Upstream HERE is
# "/home/claude/semtech-landscape" and 04-page/semtech_page_abox_v4_1_0.ttl is a
# build artefact the repository does not contain; here HERE is this example
# directory and 04-page/ holds a fixture standing in for it.  Identical
# bindings for both representations.
import os

from rdflib import Namespace

HERE = os.path.dirname(os.path.abspath(__file__))
SP = Namespace("http://example.org/semtech/page#")

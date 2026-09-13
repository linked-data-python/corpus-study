# Context shim (see meta.json): the region's `HERE` (the directory of the
# original build_page_v6_7_0.py, used to locate its sibling ABox file) is a
# path-only helper with no RDF logic of its own. We point it at a minimal
# stand-in ABox (04-page/semtech_page_abox_v6_6_0.ttl, alongside this shim)
# instead of shipping the full landscape ABox from the origin repository.
# Identical bindings for both representations.
import os

HERE = os.path.dirname(os.path.abspath(__file__))

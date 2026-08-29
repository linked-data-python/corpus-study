# Context shim (see meta.json): BASEDIR and load(), restored from
# altunelyusuf/SemanticTechnologies@bad0fa7c46
# landscape/07-tooling/build_core_v6_9_0.py, lines 10-13 -- defined earlier
# in the same source file, just outside this region's extracted line range
# (101-108), and referenced by lines already in the captured context
# (eo = load("enrichment_o", "v6_1_0"); g1 = Graph().parse(f"{BASEDIR}/...")).
# load() itself is copied verbatim. BASEDIR's real value
# ("/home/claude/semtech-landscape", the original author's own machine) is
# redirected to this shim's own landscape/ subdirectory, which holds a
# verbatim copy of enrichment_o_v6_1_0.py (the EXT8 dict this region
# iterates) and a minimal placeholder for semtech_research_v6_8_0.ttl (see
# that file's own header: this region never reads the pre-existing graph).
# Identical for both representations.
import os
import importlib.util

BASEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "landscape")


def load(name, ver):
    s = importlib.util.spec_from_file_location(name, f"{BASEDIR}/07-tooling/{name}_{ver}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m

# Context shim (see meta.json): BASEDIR and S(), restored from
# altunelyusuf/SemanticTechnologies@bad0fa7c46
# landscape/07-tooling/build_core_v5_3_0.py, lines 11 and 32 -- defined
# earlier in the same source file, just outside this region's extracted line
# range (147-155). REG here holds only the "R-TOGAF" entry that S() needs
# for this region, copied verbatim from
# landscape/07-tooling/enrichment_l_v5_3_0.py (EXT6); the full REG dict in
# the source module merges six such registries loaded from sibling files
# (tax.C, rx.EXT, ec.EXT2, eh.EXT4, eh2.EXT5, el.EXT6), none of whose other
# entries this region reads. BASEDIR's real value
# ("/home/claude/semtech-landscape", the original author's own machine) is
# redirected to this shim's own landscape/ subdirectory, which holds a
# minimal placeholder for semtech_tbox_v5_2_0.ttl (see that file's own
# header: this region never reads the pre-existing graph, only adds to it).
# Identical for both representations.
import os

BASEDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "landscape")

REG = {
    "R-TOGAF": {
        "cite": "The Open Group (2018). TOGAF Standard, Version 9.2 — Chapter 41: Architecture Board.",
        "url": "https://pubs.opengroup.org/architecture/togaf9-doc/arch/chap41.html",
    },
}


def S(*keys):
    return " | ".join(REG[k]["cite"] for k in keys)

# Context shim (see meta.json): restores `BASEDIR` and `S`, both used but
# not defined in the extracted region, from altunelyusuf/SemanticTechnologies
# @ bad0fa7c46af (landscape/07-tooling/build_core_v6_4_0.py, verified against
# the source repository at that commit).
#
# `S` is copied VERBATIM from build_core_v6_4_0.py:
#     def S(*keys): return " | ".join(REG[k]["cite"] for k in keys)
# There, `REG` is `{**tax.C, **rx.EXT, **ec.EXT2, **eh.EXT4, **eh2.EXT5,
# **el.EXT6, **em.EXT7, **eo.EXT8}`, assembled by dynamically loading ~20
# versioned modules from a hardcoded local path
# (`BASEDIR = "/home/claude/semtech-landscape"`) that does not exist here.
# Reproducing the full registry is out of a shim's scope; only the two keys
# this region actually looks up, "R-TOGAF" and "R-DAMA", are reproduced --
# copied verbatim from their real source, `EXT6` in
# landscape/07-tooling/enrichment_l_v5_3_0.py at the same commit.
#
# `BASEDIR` in the source repository names a real directory holding the
# actual semtech_tbox_v6_3_0.ttl (see 02-ontology/semtech_tbox_v6_3_0.ttl in
# this region directory for why a minimal stand-in file is enough there).
# Both sides parse the same file at the same path, so BASEDIR resolves to
# this shim's own directory.
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))

# EXT6, verbatim from enrichment_l_v5_3_0.py (only the two keys this region
# looks up; the module also defines ROLES/ACTIVITIES/RULES source data that
# this region does not read -- it writes its own hardcoded (cid, clab, cdef)
# triples instead, so nothing beyond EXT6 is in scope for this shim).
REG = {
    "R-TOGAF": {
        "cite": "The Open Group (2018). TOGAF Standard, Version 9.2 — Chapter 41: Architecture Board.",
        "url": "https://pubs.opengroup.org/architecture/togaf9-doc/arch/chap41.html",
        "level": "TOOLCHAIN-VERIFIED", "ev": "fetched in full, content confirmed 2026-08-05",
    },
    "R-DAMA": {
        "cite": "DAMA International (2026). DAMA Data Management Body of Knowledge (DAMA-DMBOK), 2nd Edition.",
        "url": "https://dama.org/learning-resources/dama-data-management-body-of-knowledge-dmbok/",
        "level": "TOOLCHAIN-VERIFIED", "ev": "fetched in full, content confirmed 2026-08-05",
    },
}


def S(*keys):
    return " | ".join(REG[k]["cite"] for k in keys)

# Context shim (see meta.json): restores `BASEDIR` and `S`, both used but
# not defined in the extracted region, from altunelyusuf/SemanticTechnologies
# @ bad0fa7c46af (landscape/07-tooling/build_core_v5_3_0.py, verified against
# the source repository at that commit).
#
# `S` is copied VERBATIM from build_core_v5_3_0.py:
#     def S(*keys): return " | ".join(REG[k]["cite"] for k in keys)
# There, `REG` is `{**tax.C, **rx.EXT, **ec.EXT2, **eh.EXT4, **eh2.EXT5,
# **el.EXT6}`, assembled by dynamically loading ~20 versioned modules from a
# hardcoded local path (`BASEDIR = "/home/claude/semtech-landscape"`) that
# does not exist here. Only the one key this region looks up, "R1", is
# reproduced, copied verbatim from its real source (`C` in
# landscape/07-tooling/taxonomy_v1_0_0.py at the same commit).
#
# `BASEDIR` names, in the source repository, the directory holding the real
# semtech_tbox_v5_2_0.ttl; here it resolves to this shim's own directory,
# which holds a minimal stand-in 02-ontology/semtech_tbox_v5_2_0.ttl (both
# sides parse the same file at the same path).
import os

BASEDIR = os.path.dirname(os.path.abspath(__file__))

REG = {
    "R1": dict(cite="Hogan, A. et al. (2021). Knowledge Graphs. ACM Computing Surveys 54(4):71, 1-37. doi:10.1145/3447772; arXiv:2003.02320.",
               url="https://arxiv.org/abs/2003.02320", level="RETRIEVED",
               ev="arXiv abstract page fetched 2026-08-04; title, lead author, venue, year confirmed (v6, 2021-09-11)."),
}


def S(*keys): return " | ".join(REG[k]["cite"] for k in keys)

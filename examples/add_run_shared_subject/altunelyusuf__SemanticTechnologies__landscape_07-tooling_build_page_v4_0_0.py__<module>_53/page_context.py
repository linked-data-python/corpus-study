# Context shim (see meta.json): the binding of
# landscape/07-tooling/build_page_v4_0_0.py that the extracted context lines
# do not carry -- HERE (line 10 of the upstream file). Upstream HERE is
# "/home/claude/semtech-landscape"; here HERE resolves to the checked-out
# repository at the pinned commit (corpus/repos/altunelyusuf__SemanticTechnologies,
# see meta.json), where 04-page/semtech_page_abox_v3_0_0.ttl is the real
# committed build artefact -- no fixture invented, the actual file is read
# verbatim by both representations.
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
HERE = os.path.join(
    _ROOT, "corpus", "repos", "altunelyusuf__SemanticTechnologies", "landscape")

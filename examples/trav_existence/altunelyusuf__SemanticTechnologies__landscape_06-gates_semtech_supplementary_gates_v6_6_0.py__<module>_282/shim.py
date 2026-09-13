# Context shim (see meta.json): minimal stand-in for the surrounding script
# altunelyusuf/SemanticTechnologies@bad0fa7c46:
# landscape/06-gates/semtech_supplementary_gates_v6_6_0.py, so the region
# executes outside the repository. HERE points at this file's directory,
# where a copy of the backlog ABox fixture lives; `feats` stands for the
# feature list built earlier in the same script. Identical bindings for
# both representations.
from pathlib import Path
from rdflib import Namespace, Graph  # noqa: F401  (re-exported for original.py)

HERE = str(Path(__file__).resolve().parent)

B2 = Namespace("http://example.org/backlog#")
feats = [B2.F1, B2.F2, B2.F3, B2.F4]

# Context shim (see meta.json): the region instantiates Nanopub, whose module
# (Nanopublication/nanopub-py@05022dc4bc, nanopub/nanopub.py) drags in the whole
# package -- definitions, namespaces, profile, serialize, sign_utils, utils.
# Reproducing any useful subset here would amount to vendoring the package, so
# this shim instead puts the corpus checkout that the evaluation already carries
# on sys.path and re-exports the three names the region imports.  Nothing is
# stubbed: the real Nanopub, NanopubConf and namespaces are used, and the region
# runs entirely offline (no profile, no key, no network call).
#
# This module is imported IDENTICALLY by original.py and translated.ldpy.
import sys
from pathlib import Path

try:  # if nanopub is installed in the environment, prefer it
    from nanopub import Nanopub, NanopubConf, namespaces  # noqa: F401
except ImportError:
    _checkout = (Path(__file__).resolve().parents[3]
                 / "corpus" / "repos" / "Nanopublication__nanopub-py")
    if str(_checkout) not in sys.path:
        sys.path.insert(0, str(_checkout))
    from nanopub import Nanopub, NanopubConf, namespaces  # noqa: F401

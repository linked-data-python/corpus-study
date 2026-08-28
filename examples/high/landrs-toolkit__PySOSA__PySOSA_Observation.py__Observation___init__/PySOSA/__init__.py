"""Context shim for `from PySOSA import config as cfg`.

Upstream PySOSA/__init__.py (landrs-toolkit/PySOSA@1993668bd7) does
`from . import *` over every module of the package; only `config` is
reachable from the region, so this stub exposes just that one.
"""

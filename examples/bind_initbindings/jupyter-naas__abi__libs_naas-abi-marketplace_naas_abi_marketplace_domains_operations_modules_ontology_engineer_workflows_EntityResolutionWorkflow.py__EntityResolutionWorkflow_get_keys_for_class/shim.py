# Context shim (see meta.json): `logger` of naas_abi_core, which is not
# installable here. In jupyter-naas/abi@3fb7f5304d, naas_abi_core/__init__.py
# exposes a module-level `logger` (a standard logging.Logger); the region
# only calls `logger.warning`. Identical binding for both representations.
import logging

logger = logging.getLogger("naas_abi_core")

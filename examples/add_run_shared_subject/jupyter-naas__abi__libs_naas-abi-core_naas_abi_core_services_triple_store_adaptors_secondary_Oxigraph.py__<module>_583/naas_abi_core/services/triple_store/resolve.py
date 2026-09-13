# Context shim (see meta.json): subset of
# naas_abi_core/services/triple_store/resolve.py from jupyter-naas/abi@3fb7f5304d,
# so the region executes outside the package. Reproduces only the two
# resolution branches reachable here (no .abi/dev/instance.json in this
# sandbox): the env-var override, then the caller's default.
# Identical bindings for both representations.
import os


def resolve_local_http_url(service, *, env_var=None, default_url, start=None):
    if env_var and os.environ.get(env_var):
        return os.environ[env_var]
    return default_url

# Context shim (see meta.json): `_pod_base` from tests/conftest.py in
# LA3D/cogitarelink-solid@49121503ea, so POD_URL resolves exactly as the
# real integration test suite does -- an env var override, defaulting to
# the real dev Pod domain the tests run against.
#
# Identical for both representations.
import os


def _pod_base() -> str:
    raw = os.environ.get("POD_URL", "https://pod.vardeman.me")
    return raw.rstrip("/")

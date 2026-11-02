# Context shim (see meta.json): `_pod_base` copied verbatim from
# LA3D/cogitarelink-solid@49121503ea, tests/conftest.py (the real module is a
# pytest root conftest, not importable as `tests.conftest` outside the
# repository). Identical bindings for both representations.
import os


def _pod_base() -> str:
    raw = os.environ.get("POD_URL", "https://pod.vardeman.me")
    return raw.rstrip("/")

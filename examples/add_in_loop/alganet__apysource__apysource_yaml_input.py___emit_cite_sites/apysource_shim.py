# Context shim (see meta.json): subset of apysource/namespaces.py and
# apysource/schema.py and the `_anon`/`_slugify` helpers of
# apysource/yaml_input.py, from alganet/apysource@f800ec97c1, so the region
# executes outside the package. Identical bindings for both representations.
import re

from rdflib import BNode, Namespace
from rdflib.namespace import PROV, RDF

SV = Namespace("https://alganet.github.io/apysource/vocab.ttl#")
OA = Namespace("http://www.w3.org/ns/oa#")

_CITE_SITE_ALLOWED = {"file", "line"}


def reject_unknown_keys(entry: dict, allowed: set, what: str) -> None:
    unknown = sorted(k for k in entry if k not in allowed)
    if unknown:
        raise ValueError(
            f"{what}: unknown key{'s' if len(unknown) > 1 else ''} "
            f"{', '.join(repr(k) for k in unknown)}. "
            f"Known keys are: {', '.join(sorted(allowed))}.",
        )


def text(value: object, what: str) -> str:
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    raise ValueError(
        f"{what} must be a single piece of text, not a "
        f"{type(value).__name__}.",
    )


def _slugify(value: str) -> str:
    slug = value.lower().strip()
    slug = re.sub(r"\W+", "_", slug, flags=re.UNICODE)
    return slug.strip("_")


def _anon(owner, role: str) -> BNode:
    return BNode(f"{_slugify(str(owner))}_{role}")

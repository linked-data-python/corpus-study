"""Driver for test_deterministic_uris (apysource).

The region loads the same YAML twice and asserts that the sorted
`sv:Source` subjects coincide. Its only observable outcome is that
assertion, so the driver makes it observable on three inputs, using a
`tmp_path` whose `write_text` writes a content of the driver's choosing:

  * identical YAML twice             -> passes (returns None)
  * YAML differing only in a fragment -> passes: the sources are equal, but
    a pattern widened beyond `sv:Source` (any typed subject) would see the
    different fragment URI and raise
  * YAML with a second source         -> AssertionError: a pattern that
    matches no source (or the wrong class) would see two empty lists and
    pass
"""
from pathlib import Path
import tempfile

from rdfeval.harness import run_pair

BASE = """\
sources:
  - label: "UN Charter"
    url: "https://www.un.org/en/about-us/un-charter/full-text"
    type: html
    language: en
    fragments:
      - label: "Preamble"
        selector: "p"
        snippet: "to save succeeding generations"
"""
OTHER_FRAGMENT = BASE.replace("Preamble", "Article 1")
TWO_SOURCES = BASE + """\
  - label: "Other Charter"
    url: "https://example.org/other"
    type: html
    language: en
"""


class _File:
    """What `tmp_path / "sources.yaml"` gives: write_text stores the next content."""

    def __init__(self, path, contents):
        self._path, self._contents = Path(path), contents

    def write_text(self, content, *a, **k):
        return self._path.write_text(self._contents.pop(0), *a, **k)

    def __fspath__(self):
        return str(self._path)

    __str__ = __fspath__


class _Dir:
    """A tmp_path whose successive writes of sources.yaml store the given contents."""

    def __init__(self, root, contents):
        self._root, self._contents = Path(root), list(contents)

    def __truediv__(self, name):
        return _File(self._root / name, self._contents)


def _case(name, *contents):
    # a fixed, per-case directory: the argument is compared across the two
    # sides, so its path must not differ between them
    root = Path(tempfile.gettempdir()) / "rdfeval_apysource" / name
    root.mkdir(parents=True, exist_ok=True)
    return lambda: ((_Dir(root, contents),), {})


VERDICT = run_pair(
    __file__,
    entry="test_deterministic_uris",
    calls=[
        _case("same", BASE, BASE),
        _case("fragment", BASE, OTHER_FRAGMENT),
        _case("sources", BASE, TWO_SOURCES),
    ],
)

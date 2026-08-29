"""The study a stage operates on.

There is **one** corpus study.  It draws code regions by **stratum of use**,
asks whether each construction of the language is useful — where, and how
often — proves construction regions by RDF isomorphism and reading regions by
the equality of the values they produce, and files its examples under
``examples/<stratum>/``.

The type survives the collapse of what used to be two studies because the
stages take it explicitly: none of them guesses which corpus it is looking
at, and the seam is where a second study would attach if one is ever needed.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import EXAMPLES_DIR


@dataclass(frozen=True)
class Study:
    name: str
    examples_dir: Path
    group: str            # the meta.json key that files an example
    suffix: str           # appended to every output file name
    # An example enters the published aggregates once a human has approved
    # it, and the counts always say "n approved of m translated".
    incremental_review: bool = True

    def path(self, base: Path) -> Path:
        """Where a stage writes, given the base name of its output."""
        if not self.suffix:
            return base
        return base.with_name(base.stem + self.suffix + base.suffix)


STUDY = Study(name="corpus", examples_dir=EXAMPLES_DIR, group="stratum",
              suffix="")

STUDIES = {"corpus": STUDY}


def get(name: str | None = None) -> Study:
    """The study; the argument is accepted and ignored for callers that
    still pass one."""
    return STUDY

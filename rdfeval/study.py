"""Which study a stage operates on.

Two studies share this pipeline and must never share a number.

``401``  files sampled by RDF density; the question is how much of the
         *construction* half of the notation the corpus absorbs; the oracle
         is RDF isomorphism; examples live under ``examples/<band>/``.
``403``  regions drawn by **stratum of use** (design record corpus/403); the
         question is whether each construction of the whole language is
         useful, where, how often; reading regions are proved by the
         equality of the values they produce (record corpus/405); examples
         live under ``examples403/<stratum>/``.

Every output file of a stage carries the study's suffix, so re-running one
study never overwrites the other's results.  A `Study` is passed explicitly:
no stage guesses which corpus it is looking at.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .config import EXAMPLES_403_DIR, EXAMPLES_DIR


@dataclass(frozen=True)
class Study:
    name: str
    examples_dir: Path
    group: str            # the meta.json key that files an example
    suffix: str           # appended to every output file name
    # 403 only: an example enters the published aggregates once a human has
    # approved it, and the counts always say "n approved of m translated".
    incremental_review: bool = False

    def path(self, base: Path) -> Path:
        """``results/raw/pairs.jsonl`` -> ``…/pairs_403.jsonl`` for study 403."""
        if not self.suffix:
            return base
        return base.with_name(base.stem + self.suffix + base.suffix)


STUDY_401 = Study(name="401", examples_dir=EXAMPLES_DIR, group="band",
                  suffix="")
STUDY_403 = Study(name="403", examples_dir=EXAMPLES_403_DIR, group="stratum",
                  suffix="_403", incremental_review=True)

STUDIES = {"401": STUDY_401, "403": STUDY_403}


def get(name: str | None) -> Study:
    return STUDIES[name or "401"]

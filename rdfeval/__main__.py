"""CLI: python -m rdfeval <stage> [options]."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .config import load_config

STAGES = ("discover", "select", "acquire", "analyze", "sample", "regions",
          "translate", "validate", "compare", "aggregate", "audit",
          "surface", "userstudy", "all")

# `all` covers the offline stages only: network stages (discover/select/
# acquire) and the human-in-the-loop stage (translate review) stay explicit.
ALL_STAGES = ("analyze", "sample", "regions", "validate", "compare",
              "aggregate", "audit", "surface", "userstudy")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rdfeval",
        description="Empirical evaluation pipeline: RDFLib corpus vs LD Python")
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("--config", default=None,
                        help="alternative evaluation.toml")
    parser.add_argument("--limit", type=int, default=None,
                        help="select: cap the number of repositories")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    config = load_config(args.config)

    def dispatch(stage: str) -> None:
        if stage == "discover":
            from . import discover
            discover.run(config)
        elif stage == "select":
            from . import select
            select.run(config, limit=args.limit)
        elif stage == "acquire":
            from . import acquire
            acquire.run(config)
        elif stage == "analyze":
            from . import corpus
            corpus.run(config)
        elif stage == "sample":
            from . import sample
            sample.run(config)
        elif stage == "regions":
            from . import regions
            regions.run(config)
        elif stage == "translate":
            from . import translate
            translate.run(config)
        elif stage == "validate":
            from . import validate
            validate.run(config)
        elif stage == "compare":
            from . import compare
            compare.run(config)
        elif stage == "aggregate":
            from . import aggregate
            aggregate.run(config)
        elif stage == "audit":
            from . import audit
            audit.run(config)
        elif stage == "surface":
            from . import surface
            surface.run(config)
        elif stage == "userstudy":
            from . import userstudy
            userstudy.run(config)

    if args.stage == "all":
        for stage in ALL_STAGES:
            print(f"=== {stage} ===")
            dispatch(stage)
    else:
        dispatch(args.stage)
    return 0


if __name__ == "__main__":
    sys.exit(main())

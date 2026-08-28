"""CLI: python -m rdfeval <stage> [options]."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .config import load_config

STAGES = ("discover", "select", "acquire", "analyze", "sample", "regions",
          "translate", "validate", "compare", "aggregate", "audit",
          "surface", "strata", "check", "status", "article", "review",
          "userstudy", "all")

# `all` covers the offline stages only: network stages (discover/select/
# acquire) and the human-in-the-loop stage (translate review) stay explicit.
ALL_STAGES = ("analyze", "sample", "regions", "validate", "compare",
              "aggregate", "audit", "surface", "strata", "userstudy")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rdfeval",
        description="Empirical evaluation pipeline: RDFLib corpus vs LD Python")
    parser.add_argument("stage", choices=STAGES)
    parser.add_argument("targets", nargs="*",
                        help="check: the example directories to verify")
    parser.add_argument("--config", default=None,
                        help="alternative evaluation.toml")
    parser.add_argument("--limit", type=int, default=None,
                        help="select: cap the number of repositories")
    parser.add_argument("--stratum", default=None,
                        help="review: restrict to one stratum")
    parser.add_argument("--set", dest="set_to", default=None,
                        choices=("approved", "rejected", "needs-work",
                                 "unreviewed"),
                        help="review: record a verdict without the loop")
    parser.add_argument("--region", default=None, help="review: with --set")
    parser.add_argument("-m", "--comment", default=None)
    parser.add_argument("--reviewer", default=None)
    parser.add_argument("--list", dest="list_only", action="store_true",
                        help="review: list what awaits review and stop")
    parser.add_argument("--run-checks", action="store_true",
                        help="status: also run the two machine checks on "
                             "every pair marked final")
    parser.add_argument("--study", choices=("401", "403"), default="401",
                        help="which study validate/compare/aggregate operate "
                             "on (401: density bands; 403: strata of use)")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    config = load_config(args.config)
    from .study import get as get_study
    study = get_study(args.study)

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
            validate.run(config, study)
        elif stage == "compare":
            from . import compare
            compare.run(config, study)
        elif stage == "aggregate":
            from . import aggregate
            aggregate.run(config, study)
        elif stage == "audit":
            from . import audit
            audit.run(config)
        elif stage == "surface":
            from . import surface
            surface.run(config)
        elif stage == "strata":
            from . import strata
            strata.run(config)
        elif stage == "review":
            from . import review
            review.run(config, study, stratum=args.stratum,
                       set_to=args.set_to, region=args.region,
                       comment=args.comment, reviewer=args.reviewer,
                       list_only=args.list_only)
        elif stage == "article":
            from . import article
            article.run(config, study)
        elif stage == "status":
            from . import status
            status.run(config, study, run_checks=args.run_checks)
        elif stage == "check":
            from . import check as check_mod
            raise SystemExit(check_mod.main(args.targets))
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

"""The incremental human review of the corpus study.

    python -m rdfeval review                 # interactive
    python -m rdfeval review --stratum remove
    python -m rdfeval review --set approved <region_id> [-m "…"]
    python -m rdfeval review --list

Design record ``corpus/403`` replaced the 401 model — review everything, then
compute — with an incremental one: the reviewer works in batches of whatever
size they like, in whatever order, and **every aggregate is recomputed on
demand over the approved subset**.  This stage is the reviewer's side of it.

What a reviewer is shown is deliberately narrow: the pair side by side, the
machine checks that already passed, and the translator's own notes.  The
machine checks are PRE-conditions — a pair that fails them never reaches a
reviewer — so the question left is the only one a machine cannot answer: *is
this the translation a competent user of the language would have written?*
"""

from __future__ import annotations

import json
import shutil
import textwrap
from datetime import datetime, timezone

from .study import Study, STUDY
from .validate import iter_examples

STATUSES = ("approved", "rejected", "needs-work", "unreviewed")


def _review_path(ex_dir):
    return ex_dir / "review.json"


def read_review(ex_dir) -> dict:
    path = _review_path(ex_dir)
    if not path.exists():
        return {"review_status": "unreviewed"}
    try:
        return json.loads(path.read_text())
    except (OSError, ValueError):
        return {"review_status": "unreadable"}


def set_status(ex_dir, status: str, comment: str | None = None,
               reviewer: str | None = None) -> dict:
    if status not in STATUSES:
        raise ValueError(f"status must be one of {STATUSES}")
    review = read_review(ex_dir)
    review.update({
        "region_id": ex_dir.name,
        "review_status": status,
        "reviewer": reviewer or review.get("reviewer"),
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "comment": comment if comment is not None else review.get("comment"),
    })
    _review_path(ex_dir).write_text(
        json.dumps(review, indent=2, ensure_ascii=False), encoding="utf-8")
    return review


def pending(study: Study, stratum: str | None = None):
    """Pairs a reviewer can act on: final, checked, not yet decided."""
    for ex_dir, meta in iter_examples(study):
        if meta.get("translation_status") != "final":
            continue
        if stratum and meta.get(study.group) != stratum:
            continue
        if read_review(ex_dir).get("review_status") in ("approved", "rejected"):
            continue
        yield ex_dir, meta


def _strip_header(text: str) -> str:
    lines = text.splitlines()
    while lines and lines[0].startswith("#"):
        lines.pop(0)
    while lines and not lines[0].strip():
        lines.pop(0)
    return lines


def side_by_side(left: list[str], right: list[str], width: int) -> list[str]:
    """Two columns, wrapped, padded — no dependency, no colour."""
    half = max(20, (width - 3) // 2)
    def cell(lines):
        out = []
        for ln in lines:
            wrapped = textwrap.wrap(ln.rstrip(), half, drop_whitespace=False,
                                    subsequent_indent="  ") or [""]
            out.extend(wrapped)
        return out
    lc, rc = cell(left), cell(right)
    rows = []
    for i in range(max(len(lc), len(rc))):
        a = lc[i] if i < len(lc) else ""
        b = rc[i] if i < len(rc) else ""
        rows.append(f"{a:<{half}} | {b}")
    return rows


def render(ex_dir, meta: dict, study: Study, width: int | None = None) -> str:
    width = width or shutil.get_terminal_size((160, 40)).columns
    review = read_review(ex_dir)
    head = [
        f"=== {meta['region_id']}",
        f"    {meta['repository']}@{meta['commit'][:10]} : {meta['path']}"
        f"  ({meta['qualname']}, lines {meta['lineno']}–{meta['end_lineno']})",
        f"    strata: {', '.join(meta.get('strata', []))}"
        f"   oracle: {meta.get('oracle', 'isomorphism')}"
        f"   classification: {meta.get('classification')}",
        f"    constructions: {', '.join(meta.get('constructions', [])) or '—'}",
        f"    review: {review.get('review_status')}",
    ]
    for note in meta.get("translation_notes", []):
        head.extend("    note: " + ln for ln in textwrap.wrap(note, width - 10))
    body = side_by_side(
        ["--- original.py (rdflib) ---", ""]
        + _strip_header((ex_dir / "original.py").read_text()),
        ["--- translated.ldpy ---", ""]
        + _strip_header((ex_dir / "translated.ldpy").read_text()),
        width)
    fixture = ex_dir / "fixture.ttl"
    tail = []
    if fixture.exists():
        tail = ["", "--- fixture.ttl (the input graph the oracle uses) ---"]
        tail += fixture.read_text().splitlines()
    return "\n".join(head + [""] + body + tail)


def run(config: dict, study: Study = STUDY, stratum: str | None = None,
        set_to: str | None = None, region: str | None = None,
        comment: str | None = None, reviewer: str | None = None,
        list_only: bool = False) -> None:
    if set_to:
        if not region:
            raise SystemExit("--set needs a region id")
        for ex_dir, meta in iter_examples(study):
            if meta["region_id"] == region:
                review = set_status(ex_dir, set_to, comment, reviewer)
                print(f"{region}: {review['review_status']}")
                return
        raise SystemExit(f"no such region: {region}")

    todo = list(pending(study, stratum))
    if list_only:
        for ex_dir, meta in todo:
            print(f"{meta[study.group]:24s} {meta['region_id']}")
        print(f"{len(todo)} pair(s) awaiting review")
        return
    if not todo:
        print("nothing to review: no pair is final, checked and undecided")
        return

    print(f"{len(todo)} pair(s) to review. "
          f"[a]pprove  [r]eject  [w]needs-work  [s]kip  [q]uit")
    for ex_dir, meta in todo:
        print()
        print(render(ex_dir, meta, study))
        try:
            answer = input("verdict [a/r/w/s/q]: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nstopped; nothing further recorded")
            return
        if answer == "q":
            return
        if answer == "s" or not answer:
            continue
        mapping = {"a": "approved", "r": "rejected", "w": "needs-work"}
        if answer not in mapping:
            print("  (not a verdict — skipped)")
            continue
        note = input("comment (optional): ").strip() or None
        set_status(ex_dir, mapping[answer], note, reviewer)
        print(f"  -> {mapping[answer]}")

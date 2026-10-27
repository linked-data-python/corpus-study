"""The agents' triage, gathered into one reading order for the reviewer.

    python -m rdfeval triage

A reviewer cannot read three hundred pairs.  Before the human review, a
*triage* agent (contract: ``AGENT_TRIAGE.md``) reads each pair and writes
``triage.json`` beside it: a priority, flags from a closed vocabulary, and
closed questions addressed to the reviewer.  This stage gathers them into

    results/review/priorities.html   high first, each linked to its digest page
    results/summary/triage.csv       one row per region, for counting

A triage verdict is advice on where to look, never a review: it does not
touch ``review.json``, and no aggregate reads it.
"""

from __future__ import annotations

import csv
import html
import json
from collections import Counter

from .config import RESULTS_SUMMARY
from .study import Study, STUDY
from .validate import iter_examples

PRIORITIES = ("high", "medium", "low")
FLAGS = ("equivalence-doubt", "weak-oracle", "shim-invents-logic",
         "wrong-construction", "classification-doubt",
         "optimization-asymmetry", "optimization-doctrine", "article-example")
TRIAGE_CSV = RESULTS_SUMMARY / "triage.csv"


def read_triage(ex_dir) -> dict | None:
    """The triage of a region, or None; an unreadable one is ``high``."""
    path = ex_dir / "triage.json"
    if not path.exists():
        return None
    try:
        triage = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return {"priority": "high", "flags": [], "questions": [],
                "summary": f"triage.json unreadable: {e}"}
    if triage.get("priority") not in PRIORITIES:
        triage["summary"] = (f"priority {triage.get('priority')!r} outside "
                             f"{PRIORITIES} — " + str(triage.get("summary")))
        triage["priority"] = "high"
    triage["unknown_flags"] = [f for f in triage.get("flags", [])
                               if f not in FLAGS]
    return triage


def collect(study: Study = STUDY) -> list[tuple]:
    """(ex_dir, meta, triage) for every final pair, triage possibly None."""
    out = []
    for ex_dir, meta in iter_examples(study):
        if meta.get("translation_status") != "final":
            continue
        if meta.get("classification") in ("not-expressible", "excluded"):
            continue
        out.append((ex_dir, meta, read_triage(ex_dir)))
    return out


def _question_html(q: dict) -> str:
    def cell(key):
        return html.escape(str(q.get(key) or ""))
    return ("<li><b>%s</b><br><span class=dim>%s</span><br>"
            "oui → %s · non → %s</li>"
            % (cell("question"), cell("where"), cell("if_yes"), cell("if_no")))


def _render(entries: list[tuple], study: Study) -> str:
    from .digest import _page
    from .review import read_review
    counts = Counter((t or {}).get("priority", "untriaged") for _, _, t in entries)
    order = {p: i for i, p in enumerate(PRIORITIES)}
    ranked = sorted((e for e in entries if e[2]),
                    key=lambda e: (order[e[2]["priority"]], e[0].name.lower()))
    rows = []
    for ex_dir, meta, triage in ranked:
        decided = read_review(ex_dir).get("review_status")
        stratum = meta.get(study.group, "?")
        link = "%s.html#%s" % (html.escape(stratum), html.escape(meta["region_id"]))
        flags = " ".join(triage.get("flags", []))
        questions = "".join(_question_html(q) for q in triage.get("questions", []))
        rows.append(
            "<tr class='%s'><td>%s</td><td>%s</td><td><a href=\"%s\">%s</a>"
            "<br><span class=dim>%s</span></td><td>%s<ul>%s</ul></td><td>%s</td></tr>"
            % (triage["priority"], triage["priority"], html.escape(stratum),
               link, html.escape(meta["region_id"]), html.escape(flags),
               html.escape(str(triage.get("summary") or "")), questions,
               html.escape(decided or "unreviewed")))
    head = ("<div class='top'><h1><a href='index.html'>digest</a> · priorities"
            "</h1><span class='count'>%d high · %d medium · %d low · "
            "%d untriaged</span></div>"
            % (counts["high"], counts["medium"], counts["low"],
               counts["untriaged"]))
    body = ("<style>.dim{color:var(--dim)} tr.high td:first-child"
            "{color:var(--danger);font-weight:bold} tr.medium td:first-child"
            "{color:var(--warn)} td{vertical-align:top;padding:.4rem}"
            "</style><p class=dim style='max-width:46rem'>Triage by agents: "
            "where to look first, never a verdict. Low-priority pairs can be "
            "approved by sampling.</p><table class='index'><thead><tr>"
            "<th>priority</th><th>stratum</th><th>region</th>"
            "<th>what to check</th><th>review</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")
    return _page("review priorities", head, body, tray=False)


def run(config: dict, study: Study = STUDY) -> None:
    from .digest import REVIEW_DIR
    entries = collect(study)
    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    out = REVIEW_DIR / "priorities.html"
    out.write_text(_render(entries, study), encoding="utf-8")
    with open(study.path(TRIAGE_CSV), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["region_id", study.group, "priority", "flags",
                    "questions", "summary"])
        for ex_dir, meta, t in entries:
            t = t or {}
            w.writerow([meta["region_id"], meta.get(study.group),
                        t.get("priority", "untriaged"),
                        " ".join(t.get("flags", [])),
                        len(t.get("questions", [])), t.get("summary", "")])
    counts = Counter((t or {}).get("priority", "untriaged") for _, _, t in entries)
    unknown = sum(bool((t or {}).get("unknown_flags")) for _, _, t in entries)
    print(f"triage: {dict(counts)} -> {out}"
          + (f" ({unknown} with flags outside the vocabulary)" if unknown else ""))

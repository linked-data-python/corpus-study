"""Export the repository funnel as a single CSV.

One row per repository *candidate* produced by ``rdfeval discover`` — not just
the ones that entered the corpus — so that the selection funnel is auditable at
a glance:

    non_examine    candidat découvert, jamais examiné
    exclu          écarté par un critère de sélection (motif en colonne)
    elague         sélectionné, cloné, puis élagué après analyse (motif)
    analyse        cloné au commit épinglé et analysé par l'analyseur AST
    controle       analysé + fichier(s) tirés dans l'échantillon de contrôle
    echantillonne  analysé + fichier(s) tirés dans l'échantillon intensif
    evalue         a fourni au moins une paire RDFLib/LD Python validée

Colonnes `etoiles`, `commits` et `dernier_commit` : étoiles, nombre de commits
et date du commit de tête de la branche par défaut, relevés par l'API GraphQL
de GitHub (`scripts/fetch_repo_stats.py`, cache `manifest/repo_stats.jsonl`).
Ce sont les valeurs du jour du relevé, pas celles du commit épinglé.

Sortie : results/summary/candidates.csv (déterministe, triée).
Usage  : python scripts/export_candidates.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from rdfeval.select import candidates, load_manifest, load_stats  # noqa: E402

OUT = ROOT / "results" / "summary" / "candidates.csv"

STATUS_RANK = {
    "evalue": 0,
    "echantillonne": 1,
    "controle": 2,
    "analyse": 3,
    "elague": 4,
    "exclu": 5,
    "non_examine": 6,
}


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    stats = load_stats()
    manifest = {r["full_name"]: r for r in load_manifest()}
    excluded = {r["full_name"]: r for r in _jsonl(ROOT / "manifest" / "excluded.jsonl")}

    sample = json.loads((ROOT / "results" / "raw" / "sample.json").read_text())
    sampled = {f["repository"] for band in sample["sample"].values() for f in band}
    control = {f["repository"] for f in sample["control"]}
    paired = {p["repository"]
              for p in _jsonl(ROOT / "results" / "raw" / "pairs.jsonl") if "region_id" in p}

    def state(name: str) -> tuple[str, str]:
        """Status and, when excluded or pruned, the reason."""
        rec = manifest.get(name)
        if rec is not None:
            if name in paired:
                return "evalue", ""
            if name in sampled:
                return "echantillonne", ""
            if name in control:
                return "controle", ""
            if rec.get("pruned"):
                return "elague", rec["pruned"]
            return "analyse", ""
        rec = excluded.get(name)
        if rec is not None:
            return "exclu", rec.get("excluded_reason", "")
        return "non_examine", ""

    rows = []
    for rec in candidates(stats):
        name = rec["full_name"]
        org, short = name.split("/", 1)
        status, motif = state(name)
        last = rec.get("last_commit") or ""
        rows.append({
            "org": org,
            "nom": short,
            "status": status,
            "motif": motif,
            "etoiles": rec.get("stars", ""),
            "commits": rec.get("commits", "") if rec.get("commits") is not None else "",
            "dernier_commit": last[:10],
            "description": (rec.get("description") or "").strip(),
            "url": rec.get("url", f"https://github.com/{name}"),
        })

    rows.sort(key=lambda r: (STATUS_RANK.get(r["status"], 9),
                             r["org"].lower(), r["nom"].lower()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["org", "nom", "status", "motif",
                                               "etoiles", "commits", "dernier_commit",
                                               "description", "url"])
        writer.writeheader()
        writer.writerows(rows)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"{OUT.relative_to(ROOT)}: {len(rows)} dépôts")
    for name in sorted(counts, key=lambda s: STATUS_RANK.get(s, 9)):
        print(f"  {name:16s} {counts[name]:5d}")


if __name__ == "__main__":
    main()

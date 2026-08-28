"""Export the repository funnel as a single CSV (org, nom, status, description, url).

One row per repository *candidate* produced by ``rdfeval discover`` — not just
the 60 that entered the corpus — so that the selection funnel is auditable at a
glance:

    non_examine  candidat découvert, jamais examiné (plafond max_repos atteint)
    exclu_*      examiné puis écarté par un critère de `[selection]`
    analyse      cloné au commit épinglé et analysé par l'analyseur AST
    controle     analysé + fichier(s) tirés dans l'échantillon de contrôle
    echantillonne  analysé + fichier(s) tirés dans l'échantillon intensif
    evalue       a fourni au moins une paire RDFLib/LD Python validée

Les colonnes `etoiles`, `commits` et `dernier_commit` viennent du cache
`manifest/repo_stats.jsonl` (voir `scripts/fetch_repo_stats.py`) : étoiles,
nombre de commits et date du commit de tête de la branche par défaut, relevés
par l'API GraphQL de GitHub. Elles sont vides si le cache est absent ou si le
dépôt n'est plus accessible. Attention : ce sont les valeurs du jour du relevé,
pas celles du commit épinglé dans le manifeste.

Sortie : results/summary/candidates.csv (déterministe, triée).
Usage  : python scripts/export_candidates.py
"""

from __future__ import annotations

import csv
import json
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results" / "summary" / "candidates.csv"

STATUS_RANK = {
    "evalue": 0,
    "echantillonne": 1,
    "controle": 2,
    "analyse": 3,
    "exclu_fork": 4,
    "exclu_metadonnees_indisponibles": 5,
    "non_examine": 6,
}


def _jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def main() -> None:
    discovery = _jsonl(ROOT / "manifest" / "discovery.jsonl")
    manifest = _jsonl(ROOT / "manifest" / "repositories.jsonl")
    excluded = _jsonl(ROOT / "manifest" / "excluded.jsonl")

    # Two seeds were renamed upstream; `select` followed the GitHub redirect and
    # stored the new name, leaving the old one as a stale discovery row. Fold it
    # into the new one so a repository is counted once (match: seed absent from
    # the manifest <-> manifest entry discovered via seed_list but not a seed).
    config = tomllib.loads((ROOT / "config" / "evaluation.toml").read_text())
    seeds = {s.lower() for s in config["discovery"]["seed_repositories"]}
    known = {r["full_name"].lower() for r in manifest + excluded}
    orphan_seeds = {s.split("/", 1)[1]: s for s in seeds if s not in known}
    renamed = {orphan_seeds[r["full_name"].split("/", 1)[1].lower()]
               for r in manifest + excluded
               if "seed_list" in r.get("strategies", [])
               and r["full_name"].lower() not in seeds
               and r["full_name"].split("/", 1)[1].lower() in orphan_seeds}

    stats = {r["full_name"].lower(): r
             for r in _jsonl(ROOT / "manifest" / "repo_stats.jsonl")}

    sample = json.loads((ROOT / "results" / "raw" / "sample.json").read_text())
    sampled = {f["repository"] for band in sample["sample"].values() for f in band}
    control = {f["repository"] for f in sample["control"]}
    paired = {p["repository"]
              for p in _jsonl(ROOT / "results" / "raw" / "pairs.jsonl") if "region_id" in p}

    def status(full_name: str) -> str:
        if full_name in paired:
            return "evalue"
        if full_name in sampled:
            return "echantillonne"
        if full_name in control:
            return "controle"
        return "analyse"

    def row(rec: dict, state: str) -> dict:
        org, name = rec["full_name"].split("/", 1)
        st = stats.get(rec["full_name"].lower(), {})
        last = st.get("last_commit") or ""
        return {
            "org": org,
            "nom": name,
            "status": state,
            "etoiles": st.get("stars") if st.get("stars") is not None else rec.get("stars", ""),
            "commits": st.get("commits") if st.get("commits") is not None else "",
            "dernier_commit": last[:10],          # AAAA-MM-JJ (UTC)
            "description": (rec.get("description") or "").strip(),
            "url": rec["url"],
        }

    rows: dict[str, dict] = {}
    # 1. every discovery candidate, a priori never examined
    for rec in discovery:
        rows[rec["full_name"].lower()] = row(rec, "non_examine")
    # 2. those examined and rejected by a selection criterion
    for rec in excluded:
        reason = rec.get("excluded_reason", "inconnu")
        if reason == "metadata_unavailable":
            reason = "metadonnees_indisponibles"
        rows[rec["full_name"].lower()] = row(rec, f"exclu_{reason}")
    # 3. those actually cloned, analysed, and possibly sampled/evaluated
    for rec in manifest:
        rows[rec["full_name"].lower()] = row(rec, status(rec["full_name"]))

    for stale in renamed:
        rows.pop(stale, None)

    ordered = sorted(rows.values(),
                     key=lambda r: (STATUS_RANK.get(r["status"], 9),
                                    r["org"].lower(), r["nom"].lower()))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["org", "nom", "status", "etoiles",
                                               "commits", "dernier_commit",
                                               "description", "url"])
        writer.writeheader()
        writer.writerows(ordered)

    counts: dict[str, int] = {}
    for row in ordered:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(f"{OUT.relative_to(ROOT)}: {len(ordered)} dépôts")
    for name in sorted(counts, key=lambda s: STATUS_RANK.get(s, 9)):
        print(f"  {name:32s} {counts[name]:5d}")


if __name__ == "__main__":
    main()

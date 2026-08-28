#!/usr/bin/env python3
"""Classe les dépôts du manifeste épinglé par famille d'usage.

Classification heuristique par mots-clés sur la description GitHub (et le
nom), une catégorie primaire par dépôt : la première règle qui matche, dans
l'ordre déclaré ci-dessous. L'ordre privilégie le spécifique (validation,
conversion) sur le générique (application). Les dépôts sans description ou
sans mot-clé reconnu restent « unclassified » — le chiffre est publié tel
quel, pas lissé.

Sortie : results/summary/repo_families.json + un tableau sur stdout.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "manifest", "repositories.jsonl")
OUT = os.path.join(ROOT, "results", "summary", "repo_families.json")

# (famille, regex sur description + nom, insensible à la casse)
RULES = [
    ("validation & quality",
     r"shacl|valid|lint|quality|conforman|compliance|checking|verif"),
    ("converters & KG construction",
     r"convert|transform|mapping|\brml\b|\betl\b|to.rdf|rdf.(export|conver)|"
     r"generat\w+ (rdf|knowledge graph|ontolog)|knowledge.?graph|harvest|"
     r"extract|ingest|pipeline|triplif|csv2|2rdf|scrap|renders|"
     r"reads.*renders|\bxmi\b"),
    ("ontology & vocabulary tooling",
     r"ontolog|vocabular|taxonom|thesaur|\bskos\b|\bowl\b|terminolog|"
     r"schema.org|controlled natural language|cidoc|\bcrm\b|data.?model|"
     r"master.?data"),
    ("SPARQL & store access",
     r"sparql|endpoint|triple.?store|triplestore|fuseki|virtuoso|graphdb|"
     r"blazegraph|query|\bquads?\b|version control for rdf|"
     r"knowledge base"),
    ("libraries & developer tools",
     r"library|\blib\b|framework|toolkit|wrapper|\bsdk\b|\bapi\b|client|"
     r"parser|serializ|plugin|utilit|helper|\bcli\b|implementation|"
     r"adapter|middleware|reader|loader|standard|\bcsvw\b|"
     r"workflow language|python classes|visuali[sz]|\bvis\b|rdflib for"),
    ("domain data & applications",
     r"biolog|biomedic|gene|protein|drug|chem|geo|spatial|map\b|museum|"
     r"heritage|archiv|librar(y|ies) catalog|bibliograph|legal|law|clinical|"
     r"health|climate|energy|sensor|iot|city|building|music|film|wiki|"
     r"lexic|linguist|corpus|dataset|data portal|catalog|metadata|"
     r"digital edition|manuscript|prosopograph|nanopub|web application|"
     r"format definition|data format|scripts|agent|audit|govern|"
     r"battery|neXtProt|biokb"),
    ("research code & experiments",
     r"paper|thesis|experiment|benchmark|reproduc|evaluation|study|"
     r"prototype|proof.of.concept|poc\b|demo|project at|course"),
]


def classify(text, has_description=True):
    if not has_description:
        return "no description"
    for family, pattern in RULES:
        if re.search(pattern, text, re.I):
            return family
    return "unclassified"


def main():
    counts = {}
    examples = {}
    n = 0
    with open(MANIFEST, encoding="utf-8") as fh:
        for line in fh:
            repo = json.loads(line)
            n += 1
            desc = repo.get("description") or ""
            text = "%s %s" % (repo.get("full_name", ""), desc)
            fam = classify(text, has_description=bool(desc.strip()))
            counts[fam] = counts.get(fam, 0) + 1
            examples.setdefault(fam, []).append(repo["full_name"])
    result = {
        "total": n,
        "method": "first-match keyword rules over GitHub description + name; "
                  "order as in scripts/classify_repos.py",
        "families": {f: {"count": counts.get(f, 0),
                         "examples": examples.get(f, [])[:5]}
                     for f, _ in RULES + [("unclassified", None),
                                          ("no description", None)]},
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=1, ensure_ascii=False)
    for f, _ in RULES + [("unclassified", None), ("no description", None)]:
        c = counts.get(f, 0)
        print("%-32s %4d  (%4.1f %%)" % (f, c, 100.0 * c / n))
    print("écrit :", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())

# Entonnoir du corpus : ce qui entre, ce qui sort, et pourquoi

Document de référence. Il répond à une question qu'on se repose à chaque
reprise — *que représente vraiment le corpus ?* — et il rassemble **tous les
critères d'exclusion**, à chaque niveau (dépôt, fichier, région, paire), avec
ce que chacun retire.

Chiffres de la vague 2 (2026-08-28, critères B7 ; `config_version` 1.0.0).
Tableau par dépôt candidat :
[`results/summary/candidates.csv`](results/summary/candidates.csv).

---

## 1. Niveau dépôt

| étape | critère | où | reste |
|---|---|---|---:|
| découverte | 4 canaux : GitHub code search (728), GitHub repo search (397), Wheelodex `rdflib` (121), liste de graines (20) ; 75 dépôts confirmés par ≥ 2 canaux | `rdfeval/discover.py` | **1 187** |
| métadonnées | licence, langages et octets, taille, dates, commits, *topics*, SHA de tête, relevés en une passe GraphQL pour **tous** les candidats | `scripts/fetch_repo_stats.py` | 1 187 |
| critères de sélection | option B7 (§ 3), appliqués candidat par candidat | `rdfeval/criteria.py` | −743 exclus |
| manifeste | les 60 dépôts de la vague 1 sont **conservés** même s'ils ne satisfont plus les critères — des traductions revues en dépendent | `rdfeval/select.py` | **444** |
| acquisition | clone `--depth 1` au commit épinglé, 8 en parallèle | `rdfeval/acquire.py` | 444 clonés, 22 Go |

Raisons d'exclusion, par candidat (un candidat peut en cumuler plusieurs) :

| raison | dépôts |
|---|---:|
| aucune licence déclarée | 460 |
| moins de 10 commits | 234 |
| aucun commit depuis 2020 | 196 |
| moins de 10 ko de Python | 114 |
| plus de 200 Mo (entrepôt de données) | 96 |
| moins de 50 ko (jouet) | 83 |
| licence non redistribuable (`NOASSERTION`, `MIT-0`, `BSD-3-Clause-Clear`) | 75 |
| matériel pédagogique | 31 |
| dépôt inaccessible (404) | 11 |
| *fork* | 9 |
| le dépôt **est** la bibliothèque (`rdflib`, `rdfextras`, `rdflib-rdfstar`) | 4 |
| miroir ou gabarit | 2 |

Le premier filtre est la **licence** : 535 candidats sur 1 187 n'ont pas de
licence permettant de republier un extrait. C'est le prix d'un corpus dont
100 % des fichiers sont échantillonnables — la vague 1 en avait 37 sur 60, et
698 de ses 1 557 fichiers RDF (45 %) étaient inéligibles pour cette seule
raison.

### Ce que le classement faisait, et ne fait plus

En vague 1, `select` triait par `(pas une graine, −nombre de canaux, −étoiles)`
et s'arrêtait à `max_repos = 60`. Comme 20 graines et 75 dépôts multi-canaux
dépassaient déjà le plafond, l'examen s'arrêtait **à l'intérieur du groupe
« ≥ 2 canaux »** : 63 dépôts examinés, **zéro** dépôt trouvé par un seul canal,
et le départage par étoiles n'a jamais fait entrer un dépôt. Le dépôt examiné
le plus étoilé en avait 623, alors que restaient dehors `topoteretes/cognee`
(30 309 ★), `datahub-project/datahub` (12 601 ★), `schemaorg/schemaorg`
(6 227 ★) — et `RDFLib/rdflib` lui-même (2 499 ★), absent de la liste de
graines.

En vague 2 le plafond (`max_repos = 500`) n'est plus atteint : **ce sont les
critères qui coupent**, pas le rang. Les 1 104 candidats mono-canal ont tous
été examinés.

### Renommages et dépôts disparus

Cinq dépôts avaient été renommés en amont (dont `oeg-upm/yatter` →
`citiususc/yatter` et `NREL/BuildingMOTIF` → `NatLabRockies/BuildingMOTIF`) :
`select` suit la redirection et enregistre le nom canonique, la ligne de
découverte périmée est repliée. **Onze** des 1 187 candidats sont aujourd'hui
inaccessibles (404 vérifié le 2026-08-28), dont deux graines :
`vemonet/sparql-void-generator`, et `RDFLib/rdflib-endpoint` — qui n'a pas
disparu mais a été transféré à `vemonet/rdflib-endpoint`, l'ancien chemin ne
redirigeant pas. La graine était périmée, pas le dépôt.

## 2. Niveau fichier

| étape | critère | où | reste |
|---|---|---|---:|
| index initial | tous les `.py` des clones | `rdfeval/corpus.py` | 58 446 |
| **environnements virtuels commités** | `exclude_dirs` : `site-packages`, `dist-packages`, `env`, `venv`, `virtualenv`, `build`, `dist`, … | `config/evaluation.toml` | −15 756 avec la limite de taille |
| **bibliothèques recopiées** | `vendored_dirs` : un répertoire de tête portant le nom d'un paquet tiers, **sauf s'il s'agit du paquet du dépôt lui-même** ; plus tout arbre `…/lib/python*/…` | `rdfeval/criteria.py` | **−3 845** dans 4 dépôts |
| taille | `max_file_bytes = 1 000 000` | `corpus.py` | **38 845 analysés** |
| non analysables | 478 fichiers Python 2 — **déclarés, pas silencieusement jetés** | `analyze.py` | 38 845 (dont 478 en erreur) |
| pertinence RDF | ≥ 1 opération RDF détectée | `analyze.py` | **6 095** |
| strate conforme | fichiers des dépôts satisfaisant les critères et non élagués | `corpus.py` | **5 190** mesurés en surface |

Les deux exclusions de niveau fichier ont la même nature — du code de
bibliothèque tiers présenté comme du code du projet — et ont été trouvées à
un mois d'intervalle :

1. **Virtualenv commité** (vague 1, fiche
   [401](../DESIGN_CHOICES/corpus/401-plan-etude-corpus.md) § Révision) :
   2 549 fichiers, 30 % de l'index initial, dont rdflib lui-même, comptés
   comme « code réel utilisant rdflib ». Aucun fichier échantillonné n'en
   venait, l'échantillon a donc été conservé.
2. **Bibliothèque recopiée hors virtualenv** (vague 2) : 3 845 fichiers dans
   quatre dépôts. `MKLab-ITI/prophet` embarque rdflib à sa racine —
   **la totalité de ses 41 fichiers RDF-pertinents** est de la bibliothèque ;
   `prrvchr/mContactOOo` et `prrvchr/uno` embarquent une distribution Python
   entière (setuptools, selenium, trio) sous `uno/lib/python/`, la disposition
   d'un virtualenv sans le marqueur `site-packages`.

L'exception « le paquet est celui du dépôt lui-même » est indispensable :
`RDFLib/sparqlwrapper` doit garder son répertoire `SPARQLWrapper/`, qui est
son propre code source.

## 3. Les critères retenus — option B7

Quinze combinaisons ont été chiffrées sur les 1 187 candidats
([`options_repo_selection.md`](options_repo_selection.md)) ; **Maxime a retenu
B7 le 2026-08-28**. Elle garde les garanties de licence et d'activité sans les
seuils de popularité et de proportion de Python, qui relèvent du goût plutôt
que de la validité.

**Premier étage**, décidable sur les seules métadonnées, avant tout clonage
(`stage1_reasons`) — un dépôt entre s'il satisfait *tous* les critères :

| critère | seuil | ce qu'il écarte |
|---|---|---|
| accessible | ni 404, ni dépôt vide | les candidats disparus depuis la découverte |
| non *fork* | `isFork = false` | les copies sans histoire propre |
| ni archivé, ni miroir, ni gabarit | | les squelettes ; les dépôts archivés restent admis |
| Python substantiel | ≥ 10 ko (≈ 250 lignes) | les projets d'un autre langage, sans clonage |
| dépôt suivi | ≥ 10 commits | les dépôts d'essai |
| taille raisonnable | 50 ko ≤ `diskUsage` ≤ 200 Mo | les jouets et les entrepôts de données |
| ni matériel pédagogique | `curso`, `course`, `tutorial`, `exercise`, `homework`, `práctica`, `student`… **en début de mot** dans le nom, la description ou les *topics* | les copies d'un même devoir par étudiant |
| ni la bibliothèque elle-même | le dépôt s'appelle `rdflib`, `rdfextras`, `rdflib-rdfstar` | `alcides/rdflib` ; **pas** pySHACL ni OWL-RL, qui sont des *clients* de rdflib |
| licence extractible | SPDX ∈ `snippet_licences` | ce dont on ne peut republier un extrait |
| vivant | dernier commit ≥ 2020-01-01 | le code abandonné avant Python 3.8 |

Le marqueur pédagogique se cherche en **début de mot** et non en sous-chaîne :
« course » est à l'intérieur de « discourse ». Un test le vérifie.

**Second étage**, après clonage et analyse (`stage2_reason`) — ces critères
demandent le code :

1. moins de 2 fichiers Python : **7 dépôts** ;
2. tout le Python est non analysable (projet Python 2) : **1 dépôt** ;
3. aucun fichier RDF-pertinent : **30 dépôts**.

Les 38 dépôts élagués **restent au manifeste** avec leur raison dans le champ
`pruned` : ils gardent la provenance des régions et paires déjà revues, mais
sortent du recensement, de l'analyse de surface et de l'échantillonnage.

### Résultat

| | vague 1 | vague 2 |
|---|---:|---:|
| dépôts au manifeste | 60 | **444** |
| dont satisfaisant les critères | 24 | **407** |
| élagués après analyse | — (critères non appliqués) | 38 |
| dépôts effectivement mesurés | 53 | **376** |
| fichiers Python analysés | 5 812 | **38 845** |
| fichiers RDF-pertinents | 1 557 | **6 095** |
| opérations RDF | 47 323 | **182 664** |
| licence permettant l'extraction | 37 / 60 | **421 / 444** |
| disque | 9 Go | 22 Go |

Les 36 dépôts de la vague 1 qui ne satisfont plus les critères ne sont pas
retirés : ils portent `selection_ok: false` et la liste des raisons. Quatre
d'entre eux ont fourni des paires validées (`MKLab-ITI/prophet`,
`maparent/virtuoso-python`, `openphacts/ops-search`,
`lawlesst/vivo-rdflib-sparqlstore`), tous écartés pour inactivité depuis 2018.

## 4. Niveau région, traduction, paire

**Cet étage date de la vague 1 et n'a pas été rejoué.** L'échantillon a été
tiré des 60 dépôts d'alors, pas des 376 mesurés aujourd'hui ; les 151
traductions revues à la main et les 140 paires prouvées équivalentes restent
valides comme mesures, mais leur population de départ est six fois plus
étroite que le corpus actuel.

Les artefacts concernés, à ne pas confondre avec des données de la vague 2 —
tous portent leur révision de pipeline dans leur champ `provenance` :

| artefact | révision | ce qu'il décrit |
|---|---|---|
| `results/raw/sample.json` | `18d6518` | 52 fichiers tirés dans 17 dépôts, graine 20260827 |
| `results/raw/regions.jsonl` | `4f2f05f` | 163 régions extraites de ces fichiers |
| `examples/<bande>/<id>/` | — | 163 dossiers, dont 151 traductions revues à la main |
| `results/raw/validation.jsonl` | `e7edab9` | 140 équivalences prouvées, 1 non résolue |
| `results/raw/pairs.jsonl`, `results/summary/pairs.csv` | `e7edab9` | 141 paires comparées |
| `results/summary/aggregate.json`, `aggregate_bands.csv`, `fig_*.{png,pdf}` | `e7edab9` | statistiques et figures dérivées de ces paires |
| `results/summary/audit.json`, `results/raw/audit_{sample,negatives}.jsonl` | `c43f8ff` | précision 0,99 et manque 12 %, jugés à la main sur la vague 1 |

En dépendent, avec les mêmes chiffres : `article/eswc/corpus_study.tex`, et les
24 tâches de `user_study/config/tasks.generated.json`.

À l'inverse, tout ce qui vient de `analyze` et de `surface`
(`files_index.jsonl`, `results/raw/analysis/`, `surface.jsonl`, `corpus.json`,
`surface.json`) porte la révision `5db2c56` ou plus récente et décrit bien les
444 dépôts.

Ces artefacts sont **conservés** : une vague 2 d'échantillonnage les complète
(`draw_wave` ajoute sans re-tirer) plutôt que de les refaire, et les
traductions déjà revues restent valides.

| étape | critère | reste |
|---|---|---:|
| échantillonnage | bandes de densité (`< 0,05` / `< 0,20` / `≥ 0,20`), quotas 12 / 16 / 24, plafond de 3 fichiers par dépôt et par bande, graine 20260827 | **52 fichiers** (+ 10 de contrôle) |
| extraction de régions | `min_rdf_ops = 2`, `max_region_loc = 120`, `coverage_threshold = 0,5` (sinon le fichier entier) | **163 régions** |
| revue humaine | quota de modèle épuisé sur les 12 dernières | **151 revues**, 12 non revues |
| classification | 108 *directly-expressible*, 25 *minor-restructuring*, 8 *awkward*, 7 *not-expressible*, 3 *excluded* | |
| comparaison | les *not-expressible* et *excluded* ne sont pas comparés | **141 paires** |
| validation | isomorphisme RDF + valeurs observables | **140 équivalentes**, 1 non résolue |

> **Point ouvert.** 44 des 141 paires (31 %) viennent de fichiers de
> `MKLab-ITI/prophet` qui sont du rdflib recopié
> (`rdflib/extras/infixowl.py`, `rdflib/plugins/sparql/sparql.py`,
> `rdflib/plugins/parsers/pyRdfa/*`). Ces fichiers ne sont plus analysés
> depuis la vague 2, mais les paires existent toujours et l'article les
> compte. Les conclusions résistent au retrait — inline-construction passe de
> +5,2 % à +6,3 % de tokens, les nœuds AST restent à +10,0 %, sur 96 paires et
> 15 dépôts au lieu de 141 et 16 — mais il faut trancher : les retirer, ou les
> garder en les déclarant comme code de bibliothèque.

## 5. Ce qui reste à faire

1. **Trancher le sort des 44 paires `prophet`** (§ 4) avant de figer
   l'article.
2. **Relever les quotas d'échantillonnage** et tirer une vague 2 de fichiers
   avec `draw_wave` : le corpus est six fois plus grand, l'échantillon ne l'est
   pas. C'est là, et pas dans la taille du corpus, que se gagne la puissance
   statistique — l'unité d'analyse est la paire validée, et trois dépôts
   fournissent aujourd'hui 103 des 141 paires.
3. **Plafonner par dépôt et par organisation dans le tirage**, pas dans la
   sélection : le risque n'est pas d'avoir huit dépôts d'un même compte dans le
   corpus, il est d'en tirer les fichiers.
4. **Séparer le recensement** plutôt que de jeter : `corpus.json` publie
   désormais les totaux complets *et* ceux de la strate conforme. Les dépôts
   de cours sont une strate, pas un déchet.
5. Refaire l'**audit de l'analyseur** (`rdfeval audit`) sur le corpus élargi :
   la précision (0,99) et le taux de manque (12 %) ont été mesurés sur la
   vague 1.

## 6. Régénérer

```bash
python scripts/fetch_repo_stats.py       # métadonnées GitHub complètes (GraphQL, cache)
python scripts/export_candidates.py      # -> results/summary/candidates.csv
python scripts/selection_options.py      # les 15 combinaisons de critères, chiffrées
python -m rdfeval select                 # critères B7 -> manifeste + excluded.jsonl
python -m rdfeval acquire                # clones parallèles au commit épinglé
python -m rdfeval analyze                # reprenable : réutilise les dépôts inchangés
python -m rdfeval surface                # formes du code, sur la strate conforme
```

`candidates.csv` : une ligne par dépôt candidat distinct (1 187), colonnes
`org, nom, status, motif, etoiles, commits, dernier_commit, description, url`.
Statuts : `evalue` 16, `echantillonne` 1, `controle` 1, `analyse` 389,
`elague` 37, `exclu` 743 — le `motif` porte la liste des critères non
satisfaits. Les trois colonnes chiffrées sont relevées au jour de l'export,
pas au commit épinglé du manifeste.

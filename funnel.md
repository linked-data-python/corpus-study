# Entonnoir du corpus : ce qui entre, ce qui sort, et pourquoi

Document de référence. Il répond à une question qu'on se repose à chaque
reprise — *pourquoi seulement 60 dépôts, et que représentent-ils vraiment ?* —
et il rassemble **tous les critères d'exclusion**, à chaque niveau
(dépôt, fichier, région, paire), qu'ils soient appliqués, déclarés mais non
appliqués, ou seulement souhaitables. Il sert à décider d'une vague suivante.

Chiffres de l'exécution du 2026-08-27/28 (`config_version` 1.0.0,
`metrics_version` 1.0.0). Tableau par dépôt :
[`results/summary/candidates.csv`](results/summary/candidates.csv),
régénéré par `python scripts/export_candidates.py`.

---

## 1. Niveau dépôt

| étape | critère | où | reste |
|---|---|---|---:|
| découverte | 4 canaux : GitHub code search (728), GitHub repo search (397), Wheelodex `rdflib` (121), liste de graines (20) ; 75 dépôts confirmés par ≥ 2 canaux | `rdfeval/discover.py` | **1 188** |
| examen | classement : graines d'abord, puis nombre de canaux, puis étoiles ; **on s'arrête au 60ᵉ retenu** | `rdfeval/select.py` | 63 examinés, **1 125 jamais examinés** |
| exclusion `fork` | `exclude_forks = true` | `select.py` | −1 (`westurner/csvw`) |
| exclusion métadonnées | dépôt inaccessible à l'API | `select.py` | −2 (`RDFLib/rdflib-endpoint`, `vemonet/sparql-void-generator`) |
| acquisition | clone `--depth 1` au commit épinglé | `rdfeval/acquire.py` | **60 dépôts analysés** |

Le corpus n'est pas petit faute de candidats : il est **plafonné**
(`max_repos = 60`). Les 1 125 candidats restants sont déjà dans
`manifest/discovery.jsonl` avec leurs métadonnées ; élargir ne demande aucune
nouvelle découverte, seulement `select` → `acquire` → `analyze` puis une vague
d'échantillonnage (`draw_wave`, qui complète au lieu de re-tirer).

### Ce que le classement a réellement fait

`select` trie par `(pas une graine, −nombre de canaux, −étoiles)`. Comme
20 graines + 75 dépôts trouvés par ≥ 2 canaux dépassent déjà le plafond de 60,
l'examen s'est arrêté **à l'intérieur du groupe « ≥ 2 canaux »** :

- 63 dépôts examinés = **20 graines + 43 multi-canaux**, et **zéro** dépôt
  trouvé par un seul canal ;
- il reste 23 candidats multi-canaux et **1 104 candidats mono-canal** jamais
  regardés ;
- le départage par étoiles n'a donc joué qu'entre multi-canaux : le nombre
  d'étoiles n'a jamais fait entrer un dépôt dans le corpus.

L'effet est visible dans `candidates.csv` : le dépôt examiné le plus étoilé a
**623 étoiles** (médiane 22, 367 commits), alors que restent dehors
`topoteretes/cognee` (30 309 ★), `datahub-project/datahub` (12 601 ★),
`schemaorg/schemaorg` (6 227 ★), `biopython/biopython` (5 176 ★),
`Accenture/AmpliGraph` (2 238 ★) — et **`RDFLib/rdflib` lui-même** (2 499 ★),
que la liste de graines ne contenait pas.

Ce n'est pas nécessairement un défaut : le cahier des charges demande
explicitement la diversité plutôt que la popularité, et un dépôt confirmé par
deux canaux est mieux attesté qu'un dépôt étoilé. Mais il faut le dire tel
quel — **le corpus est un corpus de projets moyens** (médiane 22 étoiles), et
l'absence des gros projets est un effet du classement, pas un choix motivé
projet par projet. Une vague suivante devrait réserver un quota explicite aux
candidats mono-canal fortement étoilés.

Deux graines avaient été renommées en amont (`oeg-upm/yatter` →
`citiususc/yatter`, `NREL/BuildingMOTIF` → `NatLabRockies/BuildingMOTIF`) :
`select` a suivi la redirection GitHub et enregistré le nouveau nom, laissant
l'ancien comme ligne de découverte fantôme. `export_candidates.py` replie les
deux (sinon le CSV compte 1 190 dépôts pour 1 188 réels).

`RDFLib/rdflib-endpoint` n'était pas indisponible : le projet a été transféré à
`vemonet/rdflib-endpoint` et l'ancien chemin renvoie 404 sans redirection. La
graine était donc périmée, pas le dépôt. **Onze** des 1 188 candidats sont
aujourd'hui inaccessibles (404 vérifié le 2026-08-28), dont ces deux graines.

## 2. Niveau fichier

| étape | critère | où | reste |
|---|---|---|---:|
| index initial | tous les `.py` des 60 clones | `rdfeval/analyze.py` | 8 361 |
| **environnements virtuels commités** | `exclude_dirs` : `site-packages`, `dist-packages`, `env`, `env1`, `venv`, `virtualenv`, `build`, `dist`, … | `config/evaluation.toml` | **−2 549** (30 %) |
| taille | `max_file_bytes = 1 000 000` | `analyze.py` | **5 812 analysés** |
| non analysables | 332 fichiers Python 2 (331 `SyntaxError`, 1 `TabError`) — **déclarés, pas silencieusement jetés** | `analyze.py` | 5 812 (dont 332 en erreur) |
| pertinence RDF | ≥ 1 opération RDF détectée | `analyze.py` | **1 557** |
| licence | seuls les dépôts dont la licence permet d'extraire un extrait (`snippet_licences`) peuvent être échantillonnés | `rdfeval/sample.py` | **859 éligibles** (−698) |

La contamination par virtualenv commité est la principale exclusion de niveau
fichier ; elle est documentée en détail dans
[`DESIGN_CHOICES/corpus/401`](../DESIGN_CHOICES/corpus/401-plan-etude-corpus.md)
(§ Révision du 2026-08-28) : 2 549 fichiers, dont rdflib lui-même, comptés
comme « code réel utilisant rdflib ». Aucun fichier échantillonné n'en venait
(vérifié) ; l'échantillon a donc été conservé, le fait est publié tel quel.

## 3. Niveau région, traduction, paire

| étape | critère | reste |
|---|---|---:|
| échantillonnage | bandes de densité (`< 0,05` / `< 0,20` / `≥ 0,20`), quotas 12 / 16 / 24, plafond de 3 fichiers par dépôt et par bande, graine 20260827 | **52 fichiers** (+ 10 de contrôle) |
| extraction de régions | `min_rdf_ops = 2`, `max_region_loc = 120`, `coverage_threshold = 0,5` (sinon le fichier entier) | **163 régions** |
| revue humaine | quota Opus 5 épuisé sur les 12 dernières | **151 revues**, 12 non revues |
| classification | 108 *directly-expressible*, 25 *minor-restructuring*, 8 *awkward*, 7 *not-expressible*, 3 *excluded* (base de données ou service réseau vivant requis) | |
| comparaison | les *not-expressible* et *excluded* ne sont pas comparés (10 régions listées dans `pairs.jsonl → skipped`) | **141 paires** |
| validation | isomorphisme RDF + valeurs observables | **140 équivalentes**, 1 non résolue |

---

## 4. Critères déclarés mais **jamais appliqués**

`config/evaluation.toml` annonce deux critères de sélection que `select.py`
n'implémente pas — et ne *peut* pas implémenter au moment où il s'exécute,
puisqu'ils dépendent de l'analyse, qui vient après :

- `min_python_files = 2` : **3 dépôts** retenus ne le respectent pas
  (`Coleridge-Data-For-Impact/adrf-onto` 1 fichier, `edsu/lcco` 1,
  `gnames/gnverifier` **0** — c'est un projet Go, arrivé par la liste de
  graines).
- `min_rdf_files = 1` : **7 dépôts** retenus n'ont aucun fichier RDF
  (`ag-sc/lemon.dbpedia`, `dbpedia/list-extractor`, `edsu/lcco`,
  `geopython/pygeoapi`, `gnames/gnverifier`, `michaelbrunnbauer/rdf2rdb`,
  `zincware/ZnTrack`).

Ils occupent 7 des 60 places du plafond sans rien apporter. **À faire** : une
passe d'élagage post-`analyze` qui les déplace vers `excluded.jsonl` avec la
raison, et qui libère autant de places pour la vague suivante — plutôt que de
supprimer les critères de la configuration, où ils décrivent une intention
juste.

## 5. Critères d'exclusion **manquants** (impact chiffré)

Ces quatre-là ne sont pas implémentés et biaisent aujourd'hui le recensement.

### 5.1 rdflib lui-même, et les copies vendorisées de bibliothèques

`exclude_dirs` n'attrape que les virtualenvs. Une bibliothèque tierce recopiée
à la racine d'un dépôt passe au travers :

| dépôt | arbre vendorisé | fichiers | opérations |
|---|---|---:|---:|
| `MKLab-ITI/prophet` | `rdflib/`, `isodate/`, `SPARQLWrapper/` | 129 | **878** — soit *la totalité* des opérations du dépôt |
| `mhausenblas/omnidator` | `rdflib/`, `rdfextras/`, `html5lib/` | 112 | 128 sur 142 |
| `Ebiquity/crystalia-collector` | `_vendor/` | 3 | 55 sur 134 |

Et `alcides/rdflib` (203 fichiers, 702 opérations) **est** rdflib, avec des
correctifs SQLite : ce n'est pas un usage de la bibliothèque, c'est la
bibliothèque. Le dépôt entier devrait sortir.

> **Conséquence sur les résultats publiés, à ne pas passer sous silence :**
> 5 des 52 fichiers échantillonnés sont du rdflib vendorisé dans `prophet`
> (`rdflib/extras/infixowl.py`, `rdflib/plugins/sparql/sparql.py`,
> `rdflib/plugins/parsers/pyRdfa/*`), d'où **44 des 141 paires** (31 %). Le
> filtre licence ne les a pas arrêtés : `prophet` est sous licence
> compatible, la bibliothèque recopiée dedans en hérite de fait.
>
> Les conclusions résistent au retrait (médianes, gain = positif) :
>
> | sous-groupe | n (140) | tokens | AST | n (96, hors vendorisé) | tokens | AST |
> |---|---:|---:|---:|---:|---:|---:|
> | inline-construction | 55 | +5,2 % | +10,0 % | 33 | **+6,3 %** | **+10,0 %** |
> | terms-only | 54 | +0,5 % | 0,0 % | 40 | 0,0 % | −0,4 % |
> | string-embedded | 13 | 0,0 % | −1,3 % | 6 | −11,5 % | −7,5 % |
> | no-source-rdf | 18 | 0,0 % | 0,0 % | 17 | 0,0 % | 0,0 % |
>
> Le sous-groupe *string-embedded* est celui qui bouge, et c'est déjà celui
> qui est publié comme artefact de mesure. Le nombre de dépôts contributeurs
> tombe de 16 à 15.

Critère à écrire : un répertoire de premier niveau portant le nom d'un paquet
tiers connu (`rdflib`, `rdfextras`, `isodate`, `html5lib`, `pyparsing`,
`SPARQLWrapper`, `_vendor`, `vendor`, `third_party`) est exclu **sauf s'il
s'agit du paquet du dépôt lui-même** — `RDFLib/sparqlwrapper` doit garder son
répertoire `SPARQLWrapper/`, qui est son propre code.

### 5.2 Les dépôts de cours

Cinq dépôts d'un même cours de l'Universidad Politécnica de Madrid
(`FacultadInformatica-LinkedData/Curso2021-2022`, `-ODKG`, `Curso2023-2024`,
`Curso2025-2026`, `-ODKG`) pèsent **722 fichiers, 499 fichiers RDF et 31 006
opérations, soit 65,5 % du recensement**. Ce sont des exercices d'étudiants,
souvent répétitifs, ni « bibliothèque » ni « application » ; ils sont aussi
sans licence, donc déjà inéligibles à l'échantillon.

Autrement dit : les chiffres de tête du corpus (47 323 opérations) décrivent
pour deux tiers un cours de master. **Hors cours et hors `alcides/rdflib` :
4 887 fichiers, 994 pertinents, 15 615 opérations.** Aucune paire validée n'en
provient — seul le recensement est concerné, pas les résultats.

### 5.3 Les dépôts Python 2

`ag-sc/lemon.dbpedia` (2 fichiers) et `edsu/lcco` (1) ont **100 %** de leurs
fichiers non analysables ; 14 dépôts en ont au moins un. Un dépôt dont tout le
Python est en v2 ne peut rien apporter à une étude sur une extension de
Python 3 : il devrait sortir à l'élagage post-`analyze` (§ 4), pas rester dans
le décompte des 60.

### 5.4 Les dépôts sans Python

`gnames/gnverifier` est écrit en Go (0 fichier `.py`). Il vient de la liste de
graines, qui n'a jamais été vérifiée sur ce point.

---

## 6. Critères retenus pour la vague suivante — option B7 (401 dépôts)

Quinze combinaisons de critères ont été chiffrées sur les 1 187 candidats
(comparaison complète dans
[`options_repo_selection.md`](options_repo_selection.md), de 1 130 dépôts pour
le socle à 52 pour l'attestation par deux canaux, ≈ le corpus actuel).

**Décision de Maxime, 2026-08-28 : l'option B7.** Elle garde les garanties de
licence et d'activité sans les seuils de popularité et de proportion de Python,
qui relèvent du goût plutôt que de la validité.

Premier étage, évaluable **avant clonage** sur `manifest/repo_stats.jsonl` —
un dépôt entre s'il satisfait *tous* les critères :

| critère | seuil | ce qu'il écarte |
|---|---|---|
| accessible | ni 404, ni dépôt vide | 11 candidats disparus depuis la découverte |
| non *fork* | `isFork = false` | les copies sans histoire propre |
| non archivé, ni miroir, ni gabarit | | les dépôts figés et les squelettes |
| Python présent et substantiel | ≥ 10 ko de Python (≈ 250 lignes) | les projets d'un autre langage, sans clonage — le cas `gnames/gnverifier` (Go, 0 fichier `.py`) |
| dépôt suivi | ≥ 10 commits sur la branche par défaut | les dépôts d'essai |
| taille raisonnable | 50 ko ≤ `diskUsage` ≤ 200 Mo | les jouets et les entrepôts de données (`bioregistry` pèse 1,6 Go) |
| ni matériel pédagogique | `curso`, `course`, `tutorial`, `exercise`, `homework`, `práctica`, `workshop`, `student`… dans le nom, la description ou les *topics* | les 5 dépôts de cours qui pèsent 65,5 % du recensement actuel |
| ni bibliothèque recopiée | le dépôt s'appelle `rdflib`, `rdfextras`, `sparqlwrapper`, `isodate` | `alcides/rdflib`, qui *est* rdflib |
| licence extractible | SPDX ∈ `snippet_licences` | les dépôts dont on ne peut pas republier un extrait |
| vivant | dernier commit ≥ 2020-01-01 | le code abandonné avant Python 3.8 |

Résultat : **401 dépôts**, dont 24 des 60 actuels. Tous extractibles — donc,
contrairement à aujourd'hui où 698 des 1 557 fichiers RDF (45 %) sont
inéligibles à l'échantillon pour cause de licence, **tout le corpus devient
échantillonnable**. 338 comptes GitHub distincts, au plus 8 dépôts pour un même
compte. Médiane : 6 étoiles, 129 commits, 83 % actifs depuis 2023. Coût :
≈ 12,5 Go sur disque (facteur 1,6 mesuré entre `diskUsage` et le clone
superficiel) et ≈ 32 000 fichiers Python à analyser, contre 9,0 Go et 5 812
aujourd'hui.

**Second étage, après clonage et analyse** — ces trois critères ne s'évaluent
pas sur des métadonnées :

1. `min_python_files ≥ 2` et `min_rdf_files ≥ 1` : les critères déjà déclarés
   dans `config/evaluation.toml` et jamais appliqués (§ 4), à faire respecter
   par une passe d'élagage post-`analyze` qui écrit dans `excluded.jsonl` ;
2. **aucun fichier analysable** : un dépôt dont tout le Python est en v2 sort ;
3. **arbre de bibliothèque tierce recopié** : exclusion des répertoires
   vendorisés hors virtualenv (§ 5.1), avec l'exception « le paquet est celui
   du dépôt lui-même » — `RDFLib/sparqlwrapper` garde son `SPARQLWrapper/`.

Sur le corpus actuel, 88 % des dépôts passent le second étage ; sur un vivier
plus large il faut plutôt tabler sur 70 à 85 %, soit **environ 280 à 340 dépôts
utiles** au bout de la chaîne.

Enfin, un plafond par organisation reste à fixer **au tirage** plutôt qu'à la
sélection : le risque n'est pas d'avoir 8 dépôts d'un même compte dans le
corpus, il est d'en tirer les fichiers.

## 7. Ce qu'une vague suivante devrait faire, dans l'ordre


1. **Étendre `exclude_dirs`** aux arbres vendorisés hors virtualenv (§ 5.1),
   avec l'exception « paquet du dépôt lui-même », puis re-`analyze`.
   Re-classer les 44 paires `prophet` : elles restent valides comme
   traductions, mais ne comptent plus comme code applicatif. C'est le point le
   plus urgent, parce qu'il touche des résultats déjà écrits.
2. **Implémenter B7 dans `select`** (§ 6, premier étage) et l'élagage
   post-`analyze` (second étage), les deux écrivant dans `excluded.jsonl` avec
   la raison. Sur les 60 dépôts actuels, l'élagage en retire ≈ 10.
3. **Séparer le recensement** : publier les totaux avec et sans les dépôts de
   cours plutôt que de les jeter — c'est une strate, pas un déchet, et la
   distinction est plus honnête qu'un filtre silencieux.
4. **Acquérir et analyser les 401**, puis tirer une vague 2 avec `draw_wave`
   (la graine et les fichiers déjà tirés sont conservés, les 151 traductions
   revues restent valides), avec un plafond par dépôt **et** par organisation
   dans le tirage.
5. **Relever les quotas d'échantillonnage** : c'est là, et pas dans la taille
   du corpus, que se gagne la puissance statistique — l'unité d'analyse est la
   paire validée, et trois dépôts fournissent aujourd'hui 103 des 141 paires.
6. Vérifier la liste de graines : un dépôt sans Python, un dépôt transféré.

## 8. Régénérer

```bash
python scripts/fetch_repo_stats.py       # métadonnées GitHub complètes (GraphQL, cache)
python scripts/export_candidates.py      # -> results/summary/candidates.csv
python scripts/selection_options.py      # les 15 combinaisons de critères, chiffrées
```

`candidates.csv` : une ligne par dépôt distinct (1 188), colonnes
`org, nom, status, etoiles, commits, dernier_commit, description, url`.
Statuts : `evalue` (16 — a fourni ≥ 1 paire validée), `echantillonne` (1),
`controle` (1), `analyse` (42), `exclu_fork` (1),
`exclu_metadonnees_indisponibles` (2), `non_examine` (1 125).
Les trois colonnes chiffrées sont relevées au jour de l'export, pas au commit
épinglé du manifeste.

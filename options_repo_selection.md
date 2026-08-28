# Options de sélection des dépôts : 15 combinaisons chiffrées

`funnel.md` explique pourquoi le corpus tient en 60 dépôts : un plafond
(`max_repos = 60`) atteint à l'intérieur du groupe « trouvé par ≥ 2 canaux ».
Ce fichier-ci répond à la question suivante — *si on relève le plafond, sur
quel critère arrête-t-on la liste ?* Quinze combinaisons sont évaluées sur les
**1 187 candidats distincts** de `manifest/discovery.jsonl`, avec les
métadonnées GitHub complètes (`manifest/repo_stats.jsonl`).

Reproduire : `python scripts/fetch_repo_stats.py` puis
`python scripts/selection_options.py [--markdown]`.

## Les critères testés

Tous sont évaluables **avant clonage**. Ils se lisent comme une échelle :
chaque ligne `B`*n* ajoute un critère à la précédente ; `A1`–`A3` sont des
formes alternatives, pas des durcissements de l'échelle.

- **vivant** : accessible (11 candidats renvoient 404), non *fork*, non
  archivé, ni miroir, ni gabarit, ni vide ;
- **Python présent / substantiel / majoritaire** : ≥ 1 octet, ≥ 10 ko (≈ 250
  lignes), ≥ 50 % des octets du dépôt. Ce seul critère écarte sans clonage les
  faux positifs du type `gnames/gnverifier`, projet Go arrivé par la liste de
  graines ;
- **dépôt suivi / établi** : ≥ 10 puis ≥ 50 commits sur la branche par défaut ;
- **taille raisonnable** : 50 ko ≤ `diskUsage` ≤ 200 Mo — en dessous c'est un
  jouet, au-dessus c'est un entrepôt de données (le plus gros dépôt actuel,
  `biopragmatics/bioregistry`, pèse 1,6 Go à lui seul) ;
- **ni cours ni bibliothèque recopiée** : le nom, la description ou les
  *topics* contiennent `curso`, `course`, `tutorial`, `exercise`, `homework`,
  `práctica`, `workshop`… ; ou le dépôt s'appelle comme la bibliothèque
  (`rdflib`, `rdfextras`, `sparqlwrapper`, `isodate`) ;
- **licence déclarée / extractible** : une licence SPDX explicite, puis une
  licence figurant dans `snippet_licences` — c'est elle qui décide si un
  extrait peut entrer dans les exemples publiés ;
- **activité** : dernier commit ≥ 2020, puis ≥ 2023 ;
- **visibilité** : ≥ 1 étoile ;
- **attestation** : trouvé par ≥ 2 canaux de découverte, ou publié sur PyPI
  avec une dépendance déclarée à rdflib (canal Wheelodex), ou se décrivant
  lui-même comme un projet RDF (`rdf`, `sparql`, `ontolog*`, `shacl`, `skos`,
  `knowledge graph`… dans le nom, la description ou les *topics*) ;
- **plafond par organisation** : au plus *k* dépôts d'un même compte GitHub —
  c'est ce qui aurait évité que cinq dépôts d'un même cours pèsent 65 % du
  recensement.

## Résultats, par nombre décroissant de dépôts

| option | critères | dépôts | extractibles | se disent RDF | ★ méd. | commits méd. | actif ≥ 2023 | orgs (max) | disque | des 60 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **B0 socle** | accessible, non fork, non archivé/miroir/gabarit/vide, ≥ 1 octet de Python | **1130** | 591 | 537 | 2 | 56 | 69 % | 936 (27) | 98.9 Go | 59/60 |
| **B1 Python substantiel** | B0 + ≥ 10 ko de Python (≈ 250 lignes) | **1021** | 548 | 472 | 3 | 70 | 72 % | 856 (23) | 98.1 Go | 52/60 |
| **B2 dépôt suivi** | B1 + ≥ 10 commits | **847** | 497 | 408 | 4 | 109 | 71 % | 704 (23) | 86.2 Go | 50/60 |
| **B3 taille raisonnable** | B2 + 50 ko ≤ taille ≤ 200 Mo (ni jouet, ni entrepôt de données) | **744** | 450 | 371 | 4 | 109 | 70 % | 624 (23) | 18.3 Go | 44/60 |
| **B4 ni cours ni bibliothèque recopiée** | B3 + exclusion du matériel pédagogique et des dépôts nommés comme la bibliothèque | **723** | 445 | 358 | 5 | 108 | 71 % | 613 (20) | 17.1 Go | 40/60 |
| **B5 licence déclarée** | B4 + une licence SPDX explicite | **449** | 445 | 243 | 7 | 129 | 75 % | 383 (8) | 8.6 Go | 29/60 |
| **B6 licence extractible** | B4 + licence autorisant la republication d'extraits (`snippet_licences`) | **445** | 445 | 243 | 7 | 129 | 75 % | 379 (8) | 8.6 Go | 28/60 |
| **B7 vivant depuis 2020** | B6 + dernier commit ≥ 2020-01-01 | **401** | 401 | 225 | 6 | 129 | 83 % | 338 (8) | 7.9 Go | 24/60 |
| **B8 Python majoritaire** | B7 + Python ≥ 50 % des octets du dépôt | **337** | 337 | 196 | 7 | 121 | 83 % | 287 (8) | 6.1 Go | 23/60 |
| **B9 projet établi** | B8 + ≥ 50 commits | **249** | 249 | 144 | 10 | 232 | 86 % | 217 (5) | 5.3 Go | 22/60 |
| **A3 RDF assumé, 2 par organisation** | B4 + licence extractible + le projet se décrit comme RDF + plafond de 2 dépôts par organisation | **232** | 232 | 232 | 10 | 115 | 80 % | 209 (2) | 4.3 Go | 19/60 |
| **B10 vu par quelqu'un** | B9 + ≥ 1 étoile | **216** | 216 | 134 | 14 | 238 | 85 % | 191 (5) | 4.3 Go | 22/60 |
| **B11 actif depuis 2023** | B10 + dernier commit ≥ 2023-01-01 | **184** | 184 | 117 | 16 | 266 | 100 % | 163 (4) | 4.0 Go | 20/60 |
| **A2 dépendance rdflib déclarée** | B4 + distribution PyPI déclarant rdflib (canal Wheelodex) | **87** | 69 | 29 | 2 | 122 | 92 % | 80 (4) | 1.1 Go | 7/60 |
| **A1 attesté par 2 canaux** | B4 + trouvé par ≥ 2 canaux de découverte indépendants | **52** | 35 | 36 | 23 | 218 | 71 % | 43 (9) | 0.9 Go | 34/60 |

Colonnes : *extractibles* = licence permettant de republier un extrait ;
*se disent RDF* = le projet se décrit lui-même comme un projet RDF ;
*orgs (max)* = nombre de comptes GitHub distincts, et nombre de dépôts du
compte le plus représenté ; *disque* = somme des `diskUsage` GitHub ;
*des 60* = combien des 60 dépôts actuels le critère garderait.

Le disque réel vaut environ **1,6 fois** cette estimation : les 60 dépôts
actuels totalisent 5,7 Go de `diskUsage` pour 9,0 Go sur disque (clone
superficiel + copie de travail). Compter ≈ 45 Go pour B3, ≈ 8,5 Go pour B9.
À raison de 97 fichiers Python par dépôt en moyenne (médiane 45), B9 donnerait
de l'ordre de **24 000 fichiers analysés** contre 5 812 aujourd'hui.

## Ce que les chiffres disent

**Le vivier existe.** 1 130 candidats sur 1 187 passent le socle. Le corpus à
60 n'est pas une contrainte de disponibilité : c'est un plafond arbitraire,
et la seule contrainte physique — le disque — est réglée par le critère de
taille (98,9 Go → 18,3 Go en excluant les entrepôts de données, sans perdre un
dépôt sur six).

**La licence est le vrai goulot, et elle coûte 38 %.** Passer de B4 (723) à B5
(449) élimine 274 dépôts sans licence explicite. Aujourd'hui la conséquence est
lourde : 698 des 1 557 fichiers RDF du corpus (45 %) sont inéligibles à
l'échantillon pour cette raison. Sélectionner d'emblée sur la licence donne un
corpus dont **100 % des fichiers sont échantillonnables** — 249 dépôts en B9,
tous extractibles, contre 37 sur 60 aujourd'hui.

**Le corpus actuel ≈ « attesté par 2 canaux » (A1, 52 dépôts).** C'est
exactement ce que le classement de `select` a produit, et cela explique le
profil : 23 étoiles de médiane, mais seulement 35 dépôts extractibles sur 52 et
une concentration forte (jusqu'à 9 dépôts d'un même compte). L'attestation
croisée est un bon signal de pertinence, un mauvais critère de volume.

**PyPI (A2, 87) est le critère le plus pur mais le plus étroit** : une
dépendance déclarée à rdflib dans une distribution publiée est une preuve
d'usage, pas une heuristique. Mais 87 dépôts, et une médiane de 2 étoiles —
beaucoup de petites distributions. À garder comme *strate*, pas comme filtre.

**Le plafond par organisation coûte peu et protège beaucoup** : A3 garde 232
dépôts avec au plus 2 par compte, contre 20 pour un même compte en B4. C'est
la garantie structurelle que réclame une étude statistique — les fichiers d'un
même projet ne sont pas des observations indépendantes.

## Décision, et ce qu'elle a donné

**Maxime a retenu B7, le 2026-08-28.** Les critères exacts et le second étage
post-analyse sont consignés dans `funnel.md` § 3.

Chiffres réalisés, à comparer aux 401 dépôts prévus par le tableau ci-dessus :
**444 dépôts au manifeste** (les 60 de la vague 1 sont conservés, 384 ajoutés),
dont **407 satisfont les critères** et **376 survivent à l'élagage
post-analyse**. L'écart avec la prévision vient de trois ajustements faits en
implémentant les critères : les dépôts archivés restent admis
(`exclude_archived = false`, hérité de la vague 1), le marqueur pédagogique se
cherche en début de mot et non en sous-chaîne (« course » est dans
« discourse »), et la liste des « copies de la bibliothèque » a été ramenée à
rdflib et ses forks — pySHACL et OWL-RL sont des *clients* de rdflib, donc
exactement le code que l'étude vise.

Résultat mesuré : 38 845 fichiers Python analysés, 6 095 RDF-pertinents,
182 664 opérations RDF, 22 Go sur disque. La prévision annonçait ≈ 32 000
fichiers et ≈ 12,5 Go ; le dépassement vient des dépôts de la vague 1 conservés
et de quelques projets volumineux sous le plafond de 200 Mo.

La recommandation qui suit est celle qui avait été formulée avant la décision ;
elle est conservée telle quelle.

## Recommandation (avant décision)

**B9 (249 dépôts)**, avec un plafond de 3 dépôts par organisation appliqué
ensuite. Justification : tous extractibles (donc tout le corpus est
échantillonnable, ce qui n'est pas le cas aujourd'hui), médiane de 232 commits
et 10 étoiles (des projets réels, pas des dépôts d'essai), 86 % actifs depuis
2023, ≈ 8,5 Go sur disque et ≈ 24 000 fichiers à analyser — l'analyseur passe
5 812 fichiers en quelques minutes, le facteur 4 est indolore.

Si l'on veut viser plus large sans perdre la qualité, **B7 (401)** est le
meilleur compromis : mêmes garanties de licence et d'activité, sans les seuils
de popularité et de proportion de Python qui, eux, sont des choix de goût
plutôt que des critères de validité.

Si l'on veut au contraire une strate défendable pour un argument de
généralisation, **A3 (232)** est la seule option où *chaque* dépôt se déclare
lui-même comme un projet RDF et où aucun compte ne pèse plus de deux dépôts.

## Ce que ces critères ne peuvent pas faire

Deux exclusions décisives ne s'évaluent qu'**après** clonage et analyse, et
doivent former un second étage :

1. **Aucun fichier Python pertinent** — `min_rdf_files`. Sur le corpus actuel,
   53 dépôts sur 60 (88 %) ont au moins un fichier RDF, mais ce corpus est
   biaisé par la liste de graines ; sur un vivier large, tabler plutôt sur
   70–85 %. B9 (249) donnerait donc de l'ordre de **175 à 210 dépôts** utiles.
2. **Bibliothèque tierce recopiée dans l'arbre** — le cas
   `MKLab-ITI/prophet`, qui a fourni 44 des 141 paires validées sans qu'aucune
   ne soit du code applicatif (voir `funnel.md` § 5.1). Aucun métadonné GitHub
   ne le signale : seule l'arborescence le révèle.

## L'objection à ne pas contourner

Élargir le corpus n'augmente pas mécaniquement la puissance statistique de
l'étude. **L'unité d'analyse n'est pas le dépôt, c'est la paire validée**, et
le goulot n'est ni la découverte ni le clonage : c'est la revue humaine des
traductions — 151 régions revues, à la main, ont consommé une session entière
et le quota d'un modèle. Passer de 60 à 249 dépôts sans toucher aux quotas
d'échantillonnage (12/16/24 fichiers par bande) produirait exactement le même
nombre de paires, tirées d'un vivier plus divers : **un meilleur corpus, pas
une meilleure statistique**.

Ce qui améliorerait la statistique, dans l'ordre :

1. **relever les quotas d'échantillonnage** et industrialiser la revue — c'est
   là que se gagne le *n* ;
2. **plafonner par dépôt et par organisation** dans l'échantillon, pour que les
   paires soient à peu près indépendantes : aujourd'hui 141 paires viennent de
   16 dépôts, dont trois en fournissent 103 (prophet 44, nanopub-py 34,
   pyLODE 25) — et les 44 de prophet sont du rdflib recopié ;
3. **puis seulement** élargir le corpus, qui sert alors à alimenter des quotas
   plus élevés sans re-tirer les mêmes projets.

Autrement dit, B9 est le bon corpus *à condition* d'être accompagné d'une
hausse des quotas ; sinon il ne change que la phrase de méthode.

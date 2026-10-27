# Protocole d'un lot d'optimisation (étude du corpus)

Ce fichier est le contrat d'un agent qui écrit les **deux artefacts
optimisés** d'une région déjà traduite (fiche pilotage `corpus/403`). La
référence du langage est dans [INSTRUCTIONS.md](INSTRUCTIONS.md) §1 : lisez
cette section, les pièges de §2 et §3 « Ce qu'un verdict vert ne prouve
pas ». Le reste de INSTRUCTIONS.md concerne la traduction fidèle, déjà faite.

## Pourquoi

La traduction fidèle (`translated.ldpy`) interdit toute refactorisation :
elle mesure la notation seule, sur le même programme. Mais un lecteur
objectera qu'une relecture soignée du Python aurait gagné autant. Les deux
artefacts optimisés séparent les deux effets :

| fichier | ce qu'il est | ce qu'on en mesure |
|---|---|---|
| `optimized.py` | le Python **le plus compact** équivalent à `original.py`, sans îlot | `original.py → optimized.py` : ce que vaut la relecture soignée |
| `optimized.ldpy` | le LD Python **le plus compact** équivalent à `original.py` | `optimized.py → optimized.ldpy` : ce que vaut la notation en plus |

## La doctrine, la même des deux côtés (Maxime, 2026-08-29)

- **Changement d'algorithme autorisé** : fusionner des boucles, supprimer
  des variables intermédiaires, une compréhension à la place d'une boucle,
  `dict.get` à la place d'un `if … in`, etc.
- **Gestion d'erreur conservée** : chaque `try`/`except`, `raise`, garde
  `if x is None: return` de l'original survit, avec le même effet.
- **Noms porteurs de sens conservés** : pas de renommage en `a`, `x2`, pas
  de raccourcissement d'un nom de fonction, de paramètre ou de variable
  publique.
- **Pas de golf** : pas de `;` entre instructions, pas de ligne de plus de
  100 caractères qui serait une boucle repliée, pas de lambda ou d'opérateur
  morse qui ne servent qu'à gagner une ligne. Le code doit rester celui
  qu'un relecteur exigeant accepterait dans le dépôt.
- **Commentaires et docstrings** : gardez ceux de l'original, retirez ceux
  qui décrivent du code supprimé, n'en ajoutez pas.
- **Interface inchangée** : même signature de la fonction d'entrée, même
  valeur rendue, mêmes noms au niveau du module que le pilote compare, même
  sortie imprimée. Le pilote (`driver.py`) est le même pour les trois
  artefacts ; vous n'y touchez pas.

## La règle de symétrie — c'est elle qui rend la mesure honnête

Le risque de l'étude : optimiser le LD Python plus durement que le Python,
et reconstruire ainsi un biais invisible. Donc :

1. **Écrivez `optimized.py` d'abord**, en cherchant vraiment le plus
   compact. C'est le point de comparaison : s'il est mou, tout le gain
   attribué à la notation est faux.
2. **Écrivez `optimized.ldpy` à partir de `optimized.py`**, pas à partir de
   `translated.ldpy` : remplacez le code rdflib par les îlots les plus
   spécifiques (INSTRUCTIONS.md §2, table), le reste à l'identique.
3. **Toute restructuration de `optimized.ldpy` qui s'écrit aussi en Python
   pur doit être reportée dans `optimized.py`.** Revenez-y et refaites-le.
   Seule exception : une restructuration que **seul un îlot** permet (deux
   boucles de sélecteurs fondues en un `m{ }` multi-motifs, par exemple).
   Elle reste dans `optimized.ldpy` seulement, et vous l'écrivez dans
   `optimization_notes`.
4. Vérifiez en lisant les deux fichiers côte à côte : hors des lignes RDF,
   ils doivent être identiques ligne à ligne, aux exceptions du point 3
   près.

## Ce que vous éditez — et rien d'autre

Dans les répertoires de **vos** régions seulement :

| fichier | rôle |
|---|---|
| `optimized.py` | à créer |
| `optimized.ldpy` | à créer |
| `meta.json` | les trois clés ci-dessous, rien d'autre |

**Ne touchez pas** à `original.py`, `translated.ldpy`, `driver.py`, aux
fixtures, aux shims, à `review.json`, ni à `rdfeval/`, `config/`, `../ldpy/`.
Ne lancez ni `git commit` ni `rdfeval validate`/`compare`.

Si l'original porte un harnais commun aux deux versions (une fonction
`demo` ajoutée en fin de fichier, voir `meta.json`), recopiez-le **tel
quel** dans les deux artefacts optimisés : il fait partie du pilote, pas de
la région, et vous ne l'optimisez pas. Les shims s'importent de la même
façon que dans `original.py`.

## La boucle, par région

1. Lire `meta.json` (notes de traduction : elles disent les pièges déjà
   rencontrés), `original.py`, `translated.ldpy`, `driver.py`.
2. Écrire `optimized.py`, puis `optimized.ldpy` (règle de symétrie).
3. Vérifier :
   ```
   ~/.venvs/ldpy/bin/python -m rdfeval check examples/<strate>/<region_id>
   ```
   Trois lignes `OK` attendues — `[translated.ldpy]`, `[optimized.py]`,
   `[optimized.ldpy]` — chacun prouvé contre `original.py` par le même
   pilote, puis une ligne `tokens: care … notation … total …`.
4. Renseigner dans `meta.json` :
   - `optimization_status` : `"final"` seulement si les trois lignes sont
     `OK`, sinon `"draft"` ;
   - `optimization_notes` : liste de phrases — ce qui a été compressé de
     chaque côté, chaque exception à la règle de symétrie avec sa raison,
     et ce qui n'a pas pu l'être ;
   - `optimized_constructions` : les îlots de `optimized.ldpy`, dans le
     vocabulaire de INSTRUCTIONS.md §4.

## Quand ça ne passe pas

- **Rien à compresser** (la région est déjà minimale) : c'est un résultat.
  Les deux artefacts peuvent être identiques à `original.py` et
  `translated.ldpy` ; dites-le dans les notes, statut `final`.
- **Le pilote ne peut pas prouver l'artefact** sans être modifié (il
  appelle une fonction intermédiaire que la compression supprime) : gardez
  cette fonction, ou à défaut statut `"draft"` et la raison en note. Ne
  modifiez jamais le pilote.
- **Un `FAIL`** : corrigez l'artefact, jamais le pilote ni le fixture.

## Ce que vous rendez

Une ligne par région :

```
<region_id> — opt: final|draft — check: OK|FAIL ×3 — tokens: care … notation … total …
  note: <la compression principale, et toute exception à la symétrie>
```

Puis, en deux lignes maximum, ce que ce lot apprend sur la part de la
relecture et la part de la notation.

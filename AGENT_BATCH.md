# Protocole d'un lot de traduction (étude 403)

Ce fichier est le contrat opérationnel d'un agent traducteur. Les règles de
*traduction* sont dans [INSTRUCTIONS_403.md](INSTRUCTIONS_403.md) — lisez-le
en entier avant de commencer. Ici : ce que vous éditez, comment vous
vérifiez, et ce que vous rendez.

## Environnement

- Répertoire de travail : `corpus-study/` (chemins relatifs à lui).
- Python : `~/.venvs/ldpy/bin/python` — **toujours celui-là**, jamais `python3`.
- La référence du langage : `../ldpy/docs/reference/language/*.md`
  (transpilée et exécutée par la suite de tests : elle est vraie).

## Ce que vous éditez — et rien d'autre

Uniquement les fichiers **à l'intérieur des répertoires de vos régions** :

| fichier | rôle |
|---|---|
| `translated.ldpy` | la traduction (part d'un brouillon mécanique) |
| `driver.py` | le pilote qui prouve l'équivalence |
| `fixture.ttl` | le graphe d'entrée, si la région lit |
| `original.py` | **seulement** pour rendre la région exécutable (voir plus bas) |
| `meta.json` | statut, classification, constructions employées, notes |
| `<shim>.py` | un module de contexte, si les liaisons manquent |

**N'éditez jamais** `rdfeval/`, `config/`, `../ldpy/`, ni une région qui ne
vous est pas assignée. Ne lancez ni `git commit` ni `rdfeval strata`.

## Rendre la région exécutable — le shim de contexte

Une région extraite d'un projet ne tourne pas seule : il lui manque des
imports du projet, une classe, une constante. **163 régions sur 1 196 n'ont
même pas de graphe visible** (il était lié par `self.graph` ou par un
paramètre non annoté).

Le remède est celui de l'étude 401 : un **module de contexte** à côté de la
paire, importé par `original.py`, avec un en-tête qui dit d'où il vient.

```python
# Context shim (see meta.json): subset of projet/namespaces.py from
# owner/repo@<sha>, so the region executes outside the package.
# Identical bindings for both representations.
from rdflib import Namespace
BRICK = Namespace("https://brickschema.org/schema/Brick#")
```

Pourquoi un module séparé et pas des lignes ajoutées dans `original.py` : les
métriques de surface comparent `original.py` à `translated.ldpy`. Du
échafaudage que vous auriez inventé fausserait la mesure des deux côtés. Le
shim en est exclu (il ne sert qu'à résoudre les liaisons).

Reproduisez le contexte **le plus fidèlement possible** au dépôt d'origine
(les vrais IRI, les vraies classes), en minimal. N'inventez pas de logique.

## La boucle, par région

1. **Lire** `meta.json` (provenance, strates, oracle), `original.py`, puis le
   brouillon `translated.ldpy`.
2. **Traduire** en suivant INSTRUCTIONS_403.md — la construction la plus
   spécifique, aucune refactorisation.
3. **Écrire le pilote.** Si `meta.oracle == "values"`, la région lit :
   remplissez `fixture.ttl` (plusieurs solutions, le cas zéro solution, du
   voisinage qui ne doit pas matcher) et gardez `fixture="fixture.ttl"`.
   Sinon, l'oracle est l'isomorphisme ; fournissez les arguments d'appel si
   la région est une fonction.
4. **Vérifier** :
   ```
   ~/.venvs/ldpy/bin/python -m rdfeval check examples403/<strate>/<region_id>
   ```
   Transpilation puis pilote. Itérez jusqu'à `OK`.
5. **Renseigner `meta.json`** :
   - `translation_status`: `"final"` (seulement si l'étape 4 est verte) ou
     `"draft"` si vous n'y arrivez pas ;
   - `classification`: `directly-expressible` | `minor-restructuring` |
     `awkward` | `not-expressible` | `excluded` ;
   - `constructions`: la liste des îlots employés, dans le vocabulaire de
     INSTRUCTIONS_403 §4 ;
   - `translation_notes`: ce qui a demandé un choix, et **ce qui manque** si
     une construction ne couvre pas le cas ;
   - `article_candidate`: `true` si le gain se voit en trois lignes.
   Ne touchez pas à `review.json` : la revue est humaine.

## Quand ça ne passe pas

**Ne forcez pas.** Une région que le langage ne couvre pas est un résultat de
l'étude. Dans l'ordre :

1. si la traduction est juste mais le *pilote* ne parvient pas à l'exécuter
   (dépendance externe, réseau, base de données) → `translation_status:
   "draft"`, `classification: "excluded"`, et la raison en note ;
2. si la construction existe mais rend le code plus lourd → `awkward`, avec
   le pourquoi ;
3. si rien ne couvre → `not-expressible`, avec l'extrait minimal qui le
   montre. C'est une sortie de l'étude, pas un échec.

Ne passez jamais une région en `final` sans que `rdfeval check` soit vert.

## Ce que vous rendez

Un compte rendu court, une ligne par région :

```
<region_id> — <classification> — check: OK|FAIL — constructions: …
  note: <ce qui a demandé un choix, ou ce qui manque>
```

Puis, en trois lignes maximum : ce que ce lot apprend sur la construction que
la strate devait exercer.

# Protocole d'un lot de réparation après tri (étude du corpus)

Ce fichier est le contrat d'un agent **réparateur**. Un trieur
([AGENT_TRIAGE.md](AGENT_TRIAGE.md)) a lu la paire et écrit `triage.json` :
une priorité, des drapeaux, et des questions fermées adressées à Maxime.
Beaucoup de ces questions n'ont pas besoin de lui : « le pilote n'exerce pas
le cas zéro solution », « un mutant reste vert », « la traduction échoue
quand l'entrée est une `str` ». Elles se règlent en renforçant le pilote, et
en corrigeant la traduction si le pilote renforcé la fait tomber. C'est
votre travail ; ce qui reste vraiment à juger revient à Maxime.

Python : `~/.venvs/ldpy/bin/python`. Le langage et les pièges :
[INSTRUCTIONS.md](INSTRUCTIONS.md) §1 à §3. Le protocole de traduction (ce
qu'est un pilote, un shim, un fixture) : [AGENT_BATCH.md](AGENT_BATCH.md).

## Ce que vous traitez

Les drapeaux `weak-oracle` et `equivalence-doubt` de `triage.json`. Les
autres (`wrong-construction`, `classification-doubt`,
`optimization-doctrine`, `shim-invents-logic`, `article-example`) sont des
jugements : vous ne les traitez pas, sauf une erreur matérielle de
`constructions` dans `meta.json` (un îlot déclaré qui n'est pas employé, ou
employé et non déclaré), que vous corrigez.

## La boucle, par région

1. Lire `triage.json` (questions et `evidence`), puis la paire comme le
   ferait un trieur.
2. **Renforcer le pilote d'abord, sans toucher à la traduction** : ajouter
   les appels, les branches, le cas zéro solution, le littéral `""`/`0`, le
   type d'entrée qu'emploie **réellement** le dépôt (clone sous
   `corpus/repos/`), le voisinage qui ne doit pas matcher dans le fixture,
   la comparaison de ce que la région écrit (fichier, attribut). Le pilote
   renforcé doit faire échouer les mutants que le trieur a cités : vérifiez-le
   dans une copie (`work=$(mktemp -d)`), mutant par mutant.
3. Lancer `rdfeval check` sur la région.
   - **Vert** : le doute était infondé, et il est maintenant levé par une
     preuve.
   - **Rouge sur `translated.ldpy`** : la traduction était fausse. Corrigez
     `translated.ldpy` (la construction la plus spécifique qui reste
     correcte, INSTRUCTIONS.md §2), jusqu'au vert. Si rien de correct
     n'existe dans le langage, `classification: "not-expressible"`, avec
     l'extrait minimal, et c'est un résultat de l'étude.
   - **Rouge sur un artefact optimisé** : corrigez-le de la même façon.
4. Le pilote renforcé vaut pour les trois artefacts : `check` doit rendre
   toutes ses lignes `OK` à la fin.

**Un mutant qui ne mute rien ne prouve rien** : dans rdflib 7.2.1,
`FILTER(false)` ne filtre rien (`FILTER(1 = 2)` si). Pour tuer une
branche, écrivez `FILTER(1 = 2)` ou un prédicat inexistant, et vérifiez
que le mutant change bien le résultat sur un cas simple.

Un pilote reste **lisible** : une docstring qui dit ce que chaque appel
exerce, et pourquoi. N'affaiblissez jamais un pilote, ne retirez aucun
appel existant.

## Ce que vous écrivez

Dans les répertoires de **vos** régions seulement : `driver.py`, les
fixtures, `translated.ldpy` et les artefacts optimisés s'il le faut, et
dans `meta.json` :

- `translation_notes` : ajoutez une phrase par correction de la traduction
  (ce qui était faux, la preuve) ;
- `repair` : un objet `{"date": "AAAA-MM-JJ", "driver": "ce qui a été
  ajouté au pilote", "translation_fixed": true|false, "mutants_killed":
  ["…"], "remaining": "ce qui reste à juger pour Maxime, ou vide"}`.

Dans `triage.json`, n'ajoutez qu'une clé : `"repaired": "<une phrase>"`.
Ne changez ni la priorité ni les questions : le tri reste le tri, Maxime
lira la réparation à côté.

**N'éditez pas** `original.py` (sauf pour le rendre exécutable, comme dans
AGENT_BATCH.md), les shims sauf pour fournir un type d'entrée réel,
`review.json`, ni `rdfeval/`. Ne commitez pas.

## Ce que vous rendez

```
<region_id> — driver: renforcé|inchangé — translation: corrigée|juste — check: OK|FAIL — reste: …
```

Puis, en deux lignes au plus, ce que ces réparations apprennent sur les
pilotes de la campagne.

# Protocole d'un lot de tri avant revue (étude du corpus)

Ce fichier est le contrat d'un agent **trieur**. Vous ne traduisez rien et
ne corrigez rien : vous lisez des paires déjà prouvées par la machine, et
vous dites à Maxime **lesquelles il doit regarder en premier, et quoi y
regarder**. Il ne peut pas relire 300 paires ; il relira celles que vous
mettez en tête, et approuvera les autres par sondage.

Un tri utile est **sévère et précis** : une paire mise en `high` sans raison
vérifiable lui fait perdre du temps, une paire douteuse laissée en `low`
entre dans les chiffres de l'article. Les notes du traducteur
(`translation_notes`, `optimization_notes`) sont des **affirmations à
vérifier**, pas des preuves : c'est souvent le même genre d'agent que vous
qui les a écrites.

Python : `~/.venvs/ldpy/bin/python`. Le langage : [INSTRUCTIONS.md](INSTRUCTIONS.md)
§1 (référence), §2 (constructions attendues et pièges), §3 (oracles, et
« Ce qu'un verdict vert ne prouve pas »). Les artefacts optimisés et leur
doctrine : [AGENT_OPTIMIZE.md](AGENT_OPTIMIZE.md), si la région en a.

## Ce que vous lisez, par région

`meta.json`, `original.py`, `translated.ldpy`, `driver.py`, les fixtures
(`*.ttl`), les shims (tout autre `.py`), et s'ils existent `optimized.py` et
`optimized.ldpy`. Lancez `~/.venvs/ldpy/bin/python -m rdfeval check "<dir>"`
une fois : tout doit être `OK` ; sinon c'est `high` d'office.

## Ce que vous cherchez — le vocabulaire fermé des drapeaux

| drapeau | quand le lever |
|---|---|
| `equivalence-doubt` | un cas que le pilote n'exerce pas où les deux versions se comporteraient différemment (branche, valeur `None`, graphe vide, littéral typé, ordre, cardinalité d'une jointure, BNode…) — **dites lequel** |
| `weak-oracle` | le pilote prouve peu : un seul appel pour une région à branches, fixture qui ne contient pas le cas zéro solution ni de voisinage qui ne doit pas matcher, état de module qui ne dépend pas de la région, effets non observés |
| `shim-invents-logic` | un shim ou une modification de `original.py` fait plus que restaurer des liaisons : il ajoute un comportement qui n'est pas dans le dépôt d'origine, ou retire du code de la région |
| `wrong-construction` | la traduction n'emploie pas la construction la plus spécifique (INSTRUCTIONS.md §2), ou `constructions` déclare un îlot que le code n'emploie pas (crédit indu) |
| `classification-doubt` | la classification (`directly-expressible`, `minor-restructuring`, `awkward`) ne correspond pas à ce que montre la paire |
| `optimization-asymmetry` | `optimized.ldpy` est compressé plus durement que `optimized.py` : une restructuration écrite en LD Python qui s'écrirait aussi en Python pur, et qui n'est pas dans `optimized.py` |
| `optimization-doctrine` | un artefact optimisé enfreint la doctrine : gestion d'erreur retirée, noms raccourcis, golf, interface changée |
| `article-example` | drapeau **positif** : le gain se lit en trois lignes et la paire est propre — candidate pour l'article |

### Les défauts déjà trouvés — cherchez-les d'abord

Le pilote du 2026-10-27 a trouvé, sur 14 paires toutes `final` et vertes :

1. **Le type réel de l'entrée.** Une interpolation `{expr}` coerce une `str`
   en littéral là où l'original en faisait une IRI (`<{0}>`.format) :
   regardez ce que le **dépôt d'origine** passe vraiment (le clone est sous
   `corpus/repos/<owner>__<repo>/`), pas ce que disent les notes.
2. **La véracité d'un littéral.** `not g.value(…)` traite `""` et `0` comme
   absents ; `not bool(m{ … })` et `.first() is None` non. Toute garde de
   vérité réécrite est suspecte.
3. **Le cas zéro solution et les branches secondaires** absents du pilote :
   un mutant (îlot remplacé par `[]`, prédicat échangé dans une branche)
   qui reste vert prouve que l'oracle est faible.
4. **Un nom qui disparaît d'un côté** n'est pas comparé en mode
   « module-state » (seuls les noms communs le sont).
5. **Les exceptions** : le harnais ne compare pas deux levées ; une
   réécriture qui déplace un calcul pouvant lever passe inaperçue.
6. **Les notes du traducteur** affirmaient des faits faux sur le dépôt
   (« real call sites », « verbatim », « the mirror has no source ») : un
   shim dit verbatim qui ne l'est pas, un `__namespaces__` écrit à la main
   que le dépôt n'a pas (`from … import p:` crédité indûment).
7. **Une refactorisation cachée dans la traduction fidèle** : table de
   dispatch, conditions repliées en dictionnaires, affectations hissées —
   faisables en Python pur, donc un gain que la mesure attribue à tort à la
   notation. C'est `classification-doubt` (la paire n'est pas
   `directly-expressible`), et dites-le dans la question.
8. **Des enveloppes inutiles** : `{URIRef(x)}` ou `{Literal(x)}` là où
   `f<…>` ou `{x}` passent (`wrong-construction`, vérifiez l'équivalence).

Deux défauts sont désormais **contrôlés mécaniquement** par le digest, ne
les recherchez pas à la main : l'écart entre les `constructions` déclarées
et les îlots du code, et un `__namespaces__` qu'un shim écrit alors que le
dépôt d'origine n'en exporte aucun (les 21 crédits de `from … import p:`
du corpus sont dans ce cas).

Vérifiez au lieu de supposer. Vous pouvez **expérimenter dans une copie** :
`work=$(mktemp -d)` puis `cp -r "<dir>" "$work/"` — toujours un dossier
créé par `mktemp -d`, jamais un nom fixe : d'autres trieurs travaillent en
même temps dans le même répertoire temporaire. Corrompez une ligne de la traduction ou ajouter
un appel au pilote dans la copie, et lancer `rdfeval check` sur la copie
(commande avec le chemin de la copie). Un doute confirmé par une expérience
vaut plus que dix doutes plausibles ; dites dans la question ce que
l'expérience a montré. Supprimez vos copies à la fin.

## La priorité

- **`high`** : un drapeau `equivalence-doubt`, `weak-oracle`,
  `shim-invents-logic` ou `optimization-asymmetry` que vous avez vérifié ou
  que vous pouvez montrer par une ligne précise ; ou un `check` en échec.
  Ce sont les paires qui peuvent fausser un chiffre.
  Pour `weak-oracle`, `high` exige qu'un mutant qui **supprime un îlot ou
  élargit un terme lié** reste vert. Si seuls des mutants de cardinalité
  survivent (`.first()` → `.one()`, `[:1]`) et que vous avez établi
  l'équivalence par des cas à la main, c'est `medium`.
- **`medium`** : `wrong-construction`, `classification-doubt`,
  `optimization-doctrine`, ou un drapeau `high` resté plausible sans
  preuve.
- **`low`** : rien de ce qui précède. Une paire `low` peut porter
  `article-example`.

## Ce que vous écrivez — `triage.json`, et rien d'autre

Dans le répertoire de chaque région, un seul fichier, `triage.json` :

```json
{
  "priority": "high",
  "flags": ["equivalence-doubt"],
  "summary": "Une phrase : ce qui ne va pas, ou « rien à signaler ».",
  "questions": [
    {
      "question": "Une question FERMÉE adressée à Maxime, à laquelle il répond par oui ou non.",
      "where": "translated.ldpy:14 et original.py:12",
      "if_yes": "ce que ça implique pour la paire (ex. : approuver)",
      "if_no": "ce que ça implique (ex. : needs-work, ajouter un appel au pilote avec graphe vide)"
    }
  ],
  "evidence": "Ce que vous avez exécuté pour le vérifier, et le résultat. Vide si rien.",
  "triaged_by": "sonnet-5.5"
}
```

Une question par drapeau au plus, aucune pour `low` sauf `article-example`
(« Cette paire peut-elle illustrer l'article ? »). `where` cite des fichiers
et des numéros de ligne réels.

**N'éditez rien d'autre** : ni la paire, ni `meta.json`, ni `review.json`,
ni `rdfeval/`. Ne commitez pas.

## Ce que vous rendez

Une ligne par région :

```
<region_id> — <priority> — <flags> — <summary>
```

Puis, en deux lignes au plus, un défaut qui revient d'une région à l'autre
dans ce lot, s'il y en a un.

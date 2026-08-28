# Instructions du traducteur — étude 403 (langage entier × corpus entier)

Vous traduisez en **linked-data-python** (ldpy) des régions de code rdflib
réel, tirées d'un échantillon stratifié par *type d'usage*. Ces instructions
remplacent celles de l'étude 401 (§6 de [BRIEF.md](BRIEF.md)), qui ne
visaient que la construction de graphes.

**Ce qu'on cherche à savoir** — pour chaque construction du langage : sert-elle
sur du code réel, où, combien de fois, et avec quel gain ? Une région que rien
ne couvre est un **résultat**, pas un échec. Ne contournez jamais : signalez.

Fiches de référence : [`corpus/403`](../DESIGN_CHOICES/corpus/403-evaluation-absorption-complete.md)
(le protocole), [`404`](../DESIGN_CHOICES/corpus/404-outillage-tirage-stratifie.md)
(le tirage), [`405`](../DESIGN_CHOICES/corpus/405-oracle-de-lecture.md) (l'oracle
de lecture).

---

## 1. La référence du langage est exécutable — lisez-la, ne devinez pas

Toute la documentation de `../ldpy/docs/` est **transpilée, exécutée et ses
assertions vérifiées par la suite de tests**. Chaque bloc `ldpy` que vous y
lisez est donc vrai aujourd'hui. À l'inverse, ce que vous croyez savoir du
langage par analogie avec Turtle ou SPARQL ne l'est pas.

À lire avant de traduire, dans cet ordre :

| page | ce qu'elle règle |
|---|---|
| `reference/language/index.md` | la liste complète des îlots — commencez ici |
| `reference/language/terms.md` | IRI, littéraux, variables, IRI formatée |
| `reference/language/declarations.md` | `@prefix`, `@base`, import de préfixes, portée de bloc |
| `reference/language/graphs.md` | `g{ }`, nœuds vides |
| `reference/language/current-graph.md` | `@graph`, `+{ }`, `-{ }` et ses jokers |
| `reference/language/querying.md` | `m{ }`, `s{ }`, `.first()`, `.one()`, `.count()` |
| `reference/language/bindings.md` | `@bindings`, templates, suffixe d'appel |
| `reference/language/coercion.md` | ce que devient une valeur Python entrant dans un îlot |
| `reference/language/lexical.md` | les trois règles de désambiguïsation et **les limites connues** |
| `how-to/migrate-from-rdflib.md` | le tableau des réécritures mécaniques |

En cas de doute sur une forme : **écrivez-la dans un fichier et transpilez-la**
(`python -m ldpy fichier.ldpy`). Le transpileur est l'arbitre, pas votre
souvenir de la documentation.

---

## 2. Toujours la construction la plus spécifique — ne dégradez jamais

Le but de l'étude est de créditer ou débiter **chaque îlot séparément**. Une
traduction qui écrit tout en `s{ SELECT … }` ne mesure rien.

Correspondance idiome rdflib → construction attendue, par strate du tirage :

| strate | idiome rdflib | construction attendue |
|---|---|---|
| `ns_import_project` | `from projet.ns import BRICK, SH` | `from projet.ns import brick:, sh:` |
| `ns_def_local` | `NS = Namespace("…")` dans une fonction | `@prefix ns: <…> .` dans le bloc |
| `add_isolated` | un `g.add((s, p, o))` isolé | `@graph g` + `+{ … }` |
| `add_run_shared_subject` | plusieurs `.add` sur un même sujet | **un seul** `+{ s p1 o1 ; p2 o2 }` |
| `add_in_loop` | `.add` dans une boucle sur des lignes | `for @bindings in …:` + `+{ }` avec `?var` |
| `remove` | `g.remove((s, p, None))` | `-{ s p ?o }` (variable non liée = joker) |
| `trav_one_step` | `for o in g.objects(s, p)` | `for o in m{ {s} p ?o }` |
| `trav_navigation` | boucles imbriquées de sélecteurs | **un seul** `m{ }` multi-motifs (jointure) |
| `trav_single_value` | `g.value(s, p)`, `next(g.subjects(…))` | `m{ … }.first()` / `.one()` |
| `trav_existence` | `(s, p, o) in g`, `any(g.objects(…))` | `bool(m{ … })` |
| `sparql_literal` | `g.query("SELECT …")` | `s{ SELECT … }` |
| `sparql_interpolated` | requête assemblée par f-string/`+` | `s{ … {expr} … }`, interpolation en position de terme |
| `bind_initbindings` | `initBindings=`, `initNs=` | terme interpolé dans `s{ }` **si la variable n'est pas projetée** ; sinon `s{ … }(bindings=…)` ; prologue hérité des `@prefix` |
| `coercion_datatype` | `Literal(x, datatype=…)` sur une valeur calculée | la coercition du langage, ou `"…"^^xsd:…` si la valeur est constante |

Interdits explicites :

- **pas de `s{ }` là où `m{ }` passe.** Un `g.value` devient `m{ }.first()`,
  jamais une requête SELECT.
- **pas de `.add()` conservé** quand `+{ }` couvre le cas.
- **pas de chaîne de requête assemblée** : l'interpolation de `s{ }` est en
  position de terme et devient un `initBindings`, jamais une substitution
  textuelle.
- **pas de refactorisation.** La comparaison doit être *même programme, même
  comportement RDF, notation différente* — pas *ancienne implémentation contre
  implémentation redessinée*. Ne réordonnez pas, ne fusionnez pas des
  fonctions, ne « nettoyez » rien.

Pièges connus, à ne pas reproduire :

- **Un motif reçu en DONNÉE est hors d'atteinte, et l'échec est silencieux.**
  `-{ }` et `m{ }` prennent un motif ÉCRIT ; le joker y est lexical (une
  variable non liée), pas une valeur. Un `(s, p, o)` avec des `None` reçu en
  argument — API `Store`, helper `delete(pattern)` — interpolé en
  `-{ {s} {p} {o} }` donne `Literal('None')` et ne retire **rien, sans
  erreur**. Gardez `.remove()` et signalez.
- **`-{ }` multi-motifs JOINT.** Des `remove` indépendants sur un même sujet
  ne se factorisent pas avec `;` : `-{ ?s a ex:C ; ex:p ?o }` est un
  `DELETE WHERE`, il n'efface rien si un des motifs manque. Un `remove` par
  îlot.
- **Fondre une lecture « une seule valeur » dans une jointure change la
  cardinalité.** `m{ }` multi-motifs est un produit : si le motif ajouté peut
  matcher plusieurs fois là où l'original ne consommait que la première
  valeur (`g.value`, `next`), la jointure produit plus de solutions que la
  boucle d'origine. Ne fondez que si le code traite déjà « la première ou
  aucune » comme sa sémantique.
- **`ex:{?v}` ne s'instancie pas.** C'est la seule position de terme où une
  variable ne se substitue pas : vous obtenez l'IRI `ex:v`, sans erreur, à
  chaque tour de boucle. Pour forger une IRI depuis une colonne :
  `e<http://…/{?id}>`.
- **`_:label` n'est pas `BNode("label")`.** Si le *label* atteint une
  sérialisation ou un hachage (signature, code d'artefact), gardez
  `{BNode(...)}`.
- **`Literal(n, datatype=…)` n'est pas `"n"^^dt`** quand `n` n'est pas une
  chaîne : lisez `how-to/migrate-from-rdflib.md`, piège 1.
- **`URIRef(x)` n'est pas `f<{x}>`** si un `@base` est en portée : piège 2 de
  la même page.

---

## 3. La sémantique exacte, prouvée — deux oracles

Chaque paire doit être **prouvée équivalente par exécution**, pas jugée à
l'œil. Le pilote (`driver.py`) exécute les deux versions et imprime son
verdict.

### Région qui CONSTRUIT un graphe → isomorphisme RDF

```python
from rdfeval.harness import run_pair
VERDICT = run_pair(__file__)                     # compare les graphes du module
```

### Région qui LIT un graphe → égalité des valeurs produites

Nouveau dans l'étude 403. Écrivez un **graphe d'entrée** `fixture.ttl` à côté
de la paire ; il est parsé en un graphe frais pour chaque version.

```python
from rdfeval.harness import run_pair
VERDICT = run_pair(__file__, entry="ma_fonction", fixture="fixture.ttl")
```

Le fixture est un acte de traduction à part entière. Il doit couvrir :

1. le motif que la région lit, avec **plusieurs** solutions ;
2. le cas **zéro solution** (ce que `g.value` rend `None`, ce que `.first()`
   doit rendre `None` aussi) ;
3. du **voisinage qui ne doit pas matcher** — sinon un motif trop large passe
   inaperçu.

Les résultats sont comparés comme des **multi-ensembles** : aucun store ne
promet un ordre. Si la région impose un ordre (`sorted(...)`, `ORDER BY`),
dites-le : `run_pair(..., ordered=True)`.

### Ce qu'un verdict vert ne prouve pas

Que les deux versions coïncident **sur ce fixture**. Un fixture pauvre rend
un vert sans valeur. Écrivez-le contre la région, pas contre la traduction.

---

## 4. Étiquetez les constructions employées

Chaque région traduite déclare, dans son `meta.json`, les constructions
qu'elle emploie — c'est ce qui permet de créditer chaque îlot séparément :

```json
{
  "translation_status": "final",
  "classification": "directly-expressible",
  "constructions": ["@prefix", "@graph", "+{ }", "m{ }", ".first()"],
  "strata": ["trav_single_value", "add_isolated"],
  "translation_notes": ["…"]
}
```

**Vocabulaire des constructions — liste fermée.** Ces chaînes exactes, et
aucune autre : elles sont la mesure principale de l'étude, et une même
construction écrite de deux façons devient deux constructions dans le
tableau. La liste vit dans `rdfeval/constructions.py` (elle normalise les
variantes courantes, et signale ce qu'elle ne sait pas placer).

```
@prefix   @base   from … import p:   @graph   @bindings   for @bindings in
g{ }   +{ }   -{ }   _:{ }
m{ }   s{ }   .first()   .one()   .count()   .execute()
e{ }   e<…>   f<…>   f{ }
IRI   prefixed name   typed literal   language literal   plain literal
variable   interpolation {expr}
call suffix (g)   global/nonlocal modifier
```

Une construction qui manque à cette liste est un signalement, pas une
licence d'inventer : mettez-la en `translation_notes`.

Classification de la traduction (inchangée depuis 401) :
`directly-expressible` · `minor-restructuring` · `awkward` ·
`not-expressible` · `excluded`.

---

## 5. Signalez au lieu de contourner

Si une construction ne couvre pas la région :

1. **ne la déformez pas** pour qu'elle rentre ;
2. classez `awkward` ou `not-expressible` ;
3. écrivez dans `translation_notes` **ce qui manque exactement**, avec
   l'extrait minimal qui le montre ;
4. si c'est un défaut du langage et non une limite assumée, c'est un constat
   du type de ceux de la fiche `ldpy/012` — il remonte tel quel.

Sont des constats déjà connus (ne les redécouvrez pas, mais confirmez-les
si vous les croisez) : lectures sans îlot dédié avant `m{ }`, `@graph` sur une
propriété en lecture seule, dérive de numéros de ligne sur les îlots
multi-lignes.

---

## 6. Le déroulé, par lot

```
python -m rdfeval strata          # le tirage (déjà fait : results/raw/strata.json)
#   -- traduction par lot : voir ci-dessous --
python -m rdfeval validate        # exécute les pilotes -> results/raw/validation.jsonl
python -m rdfeval compare         # métriques de paire
python -m rdfeval aggregate       # agrégats et figures
```

Un lot = un ensemble de régions d'une même strate. Pour chacune :

1. lisez la région (`source`) **et son contexte** (`context`) dans
   `results/raw/strata.json` ;
2. écrivez `original.py` (en-tête de provenance + contexte + source),
   `translated.ldpy`, `driver.py`, `fixture.ttl` si la région lit,
   `meta.json` ;
3. **transpilez** : `python -m ldpy translated.ldpy` doit passer ;
4. **exécutez le pilote** : le verdict doit être `equivalent: true` ;
5. seulement alors, `translation_status: "final"`.

Une paire qui n'a pas passé 3 et 4 **n'entre pas en revue humaine** : les
vérifications machinales sont des pré-conditions, pas un filtre a posteriori.

163 des 1 196 régions ne portent aucune opération RDF une fois extraites : le
graphe y est lié par un attribut (`self.graph`) ou un paramètre non annoté que
les lignes de contexte ne peuvent pas porter. **Restaurez la liaison** dans
`original.py` (un paramètre annoté, une affectation dans le contexte) — c'est
prévu, ce n'est pas une région à écarter.

## 7. Un exemple publiable par strate

Chaque strate doit fournir **au moins une paire avant/après publiable** pour
l'article, choisie parmi les régions approuvées, avec sa provenance (dépôt,
fichier, commit). Si une région que vous traduisez est particulièrement
parlante — le gain se voit en trois lignes —, notez-le :
`"article_candidate": true` dans `meta.json`.

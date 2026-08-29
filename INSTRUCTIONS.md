# Instructions du traducteur — l'étude du corpus

Vous traduisez en **linked-data-python** (ldpy) des régions de code rdflib
réel, tirées d'un échantillon stratifié par *type d'usage*.

**Ce qu'on cherche à savoir** — pour chaque construction du langage : sert-elle
sur du code réel, où, combien de fois, et avec quel gain ? Une région que rien
ne couvre est un **résultat**, pas un échec. Ne contournez jamais : signalez.

Fiches de référence : [`corpus/403`](../corpus/403-evaluation-absorption-complete.md)
(le protocole), [`404`](../corpus/404-outillage-tirage-stratifie.md)
(le tirage), [`405`](../corpus/405-oracle-de-lecture.md) (l'oracle
de lecture). Vous n'avez pas à les lire pour traduire : tout ce qui vous est
nécessaire est ci-dessous.

---

## 1. Le langage, en entier, ici

Cette section remplace la lecture des neuf pages de `../ldpy/docs/reference/`
(~8 500 mots) que ces instructions imposaient autrefois. Elle est
**engendrée**, pas recopiée : elle ne peut pas dériver du langage réel.

<!-- BEGIN island-reference (generated: sync_language_reference.py) -->

**Déclarations**

| forme | ce que c'est |
|---|---|
| `@prefix ex: <IRI> .` | Binds `ex:` to a namespace IRI for the rest of the enclosing block. A prefix is lexical: it has no run-time object, and `ex:` on its own is never a value. Declaring it again in a deeper block shadows it, the way a Python name would. |
| `@base <IRI> .` | Sets the base against which relative IRIs are resolved for the rest of the block, so that `<sensor/1>` means `<IRI>sensor/1`. |
| `from MODULE import ex:, unit: as u:` | Imports prefixes declared by another module, optionally renaming them. The module is imported as usual; what travels is the prefix bindings, which have no value to import by ordinary means. |
| `@graph EXPR \| @graph as NAME -> Graph` | Designates the current graph for the block — the one `+{ }`, `-{ }` and a receiver-less `m{ }` act on. `as NAME` creates a fresh graph and binds it to NAME; `global` and `nonlocal` widen the scope. |
| `@bindings EXPR \| @bindings as NAME -> Bindings` | Designates the current bindings: the mapping that gives `?name` its value in the enclosing block. Any mapping will do, and `as NAME` creates an empty one. |
| `for @bindings [as NAME] in ITER:` | Loops over an iterable of mappings, making each row the current bindings for the body. A `csv.DictReader` and the solutions of `m{ }` are both iterables of mappings, so both drive this loop. |

**Termes**

| forme | ce que c'est |
|---|---|
| `<IRI> -> URIRef` | An absolute IRI, or a relative one resolved against the `@base` in scope. |
| `ex:local -> URIRef` | A prefixed name: the local part is appended to the IRI bound to `ex:`. Turtle's character set applies inside an island, so `o-pizza:topping` and `ex:café` are names here although neither is a legal Python expression. `ex:{expr}` computes the local part. |
| `"..."@lang \| "..."^^dt -> Literal` | An RDF literal carrying a language tag or a datatype. The quoted part may be an f-string, and `{expr}` may supply the datatype itself. |
| `?name \| $name -> Variable` | A SPARQL variable. In a pattern it is what gets matched and projected; in `g{ }` or `+{ }` it takes its value from the current bindings, and leaves the triple out when it has none. |
| `f<...{expr}...> -> URIRef` | A formatted IRI: the braces interpolate as in an f-string, the result is percent-encoded and then resolved against `@base`. Encoding first is what keeps a space or a slash in a value from changing the IRI's structure. |
| `f{expr} \| ?{expr} -> Node` | Coerces any Python value into an RDF term, by the coercion policy in scope. Two spellings of one operation: `?{ }` reads better in term position, `f{ }` beside `f<...>`. |
| `_:{expr} -> BNode` | A blank node whose identity is its data: the same value gives the same node anywhere in the program, so two rows that share a key join without inventing an IRI for them. |

**Graphes et graphe courant**

| forme | ce que c'est |
|---|---|
| `g{ ... } -> Graph` | Builds an RDF graph from Turtle written in place. `{expr}` interpolates a Python value in term position, and each occurrence is evaluated once. The braces are an expression, so a `g{ }` goes anywhere a value goes — a default argument, a comprehension, a return. |
| `+{ ... } [ (GRAPH) ]` | Adds the triples to the current graph. `?name` takes its value from the current bindings, and a triple with an unbound variable is dropped rather than written half-way. A trailing `(g)` names another receiver. |
| `-{ ... } [ (GRAPH) ]` | Removes from the current graph every triple matching the pattern. An unbound variable is a wildcard here, not a hole: this is a SPARQL `DELETE WHERE`, not a list of triples to subtract. |

**Lecture**

| forme | ce que c'est |
|---|---|
| `m{ ... } -> Solutions` | Matches a basic graph pattern against the current graph, lazily. Iterating yields a bare term when one variable is projected and a tuple otherwise; `.one()`, `.first()`, `.count()` and `bool()` are the usual reductions. A `(graph)` suffix names another source. |
| `s{ ... } -> Query` | A SPARQL query or update, parsed when the file is transpiled rather than at run time. `{expr}` in term position becomes an initial binding — never string pasting, so nothing here can be injected. Call it on a graph to run it; `.execute()` runs an update. |

**Évaluation différée**

| forme | ce que c'est |
|---|---|
| `e{ ... } -> Expr` | A deferred SPARQL expression. It is not evaluated where it is written, but against the bindings in force when the island holding it is instantiated — once per row of a `for @bindings` loop. `{python}` holes are evaluated where they are written. |
| `e<...{?var}...> -> Expr` | A deferred IRI: `f<...>`'s interpolation, except that the holes are SPARQL expressions re-evaluated for each set of bindings. |

*(Engendré depuis `ldpy/lsp/islanddoc.py` — la table que le survol de l'éditeur affiche, en anglais comme tout le code. `ldpy/tests/test_islanddoc.py` garantit qu'elle décrit **toutes** les sortes d'îlot et que chacun de ses liens tombe sur une ancre vivante de la documentation. Ne l'éditez pas à la main : `python scripts/sync_language_reference.py`.)*

<!-- END island-reference -->

Trois choses que le tableau ne dit pas et qui décident de la plupart des
traductions :

- **la règle d'adjacence.** Un îlot n'ouvre que si le sigil touche
  l'accolade : `e{` ouvre, `e {` non ; `euler + 1` reste du Python. De même
  `{ex:b2}` est un ensemble contenant une IRI, alors que `{ex : b2}` est un
  dictionnaire. En cas de doute, écrivez la forme dans un fichier et
  transpilez-la.
- **un îlot est une expression.** `g{ … }` va partout où une valeur va :
  argument par défaut, compréhension, `return`, lambda. `+{ }` et `-{ }`
  sont des *instructions*, y compris en suite d'un `if` d'une ligne.
- **le transpileur est l'arbitre.** `python -m ldpy fichier.ldpy` tranche
  toute question de forme, et il tranche plus vite que la documentation. Ce
  que vous croyez savoir par analogie avec Turtle ou SPARQL n'est pas fiable.

Pour aller plus loin sur un point précis — et seulement alors — la
documentation est à `../ldpy/docs/` : `reference/language/lexical.md` pour les
trois règles de désambiguïsation et les limites connues,
`how-to/migrate-from-rdflib.md` pour le tableau des réécritures mécaniques
avec leurs pièges. Toute la documentation est transpilée, exécutée et ses
assertions vérifiées par la suite de tests : ce qu'elle montre est vrai
aujourd'hui.

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
- **`ex:{?v}` concatène sans encoder** (il s'instancie depuis 0.4.0, voir
  §2 bis). Pour forger une IRI depuis une colonne qui peut contenir une
  espace ou une barre oblique, c'est `e<http://…/{?id}>` qui encode.
- **`_:label` n'est pas `BNode("label")`.** Si le *label* atteint une
  sérialisation ou un hachage (signature, code d'artefact), gardez
  `{BNode(...)}`.
- **`Literal(n, datatype=…)` n'est pas `"n"^^dt`** quand `n` n'est pas une
  chaîne : lisez `how-to/migrate-from-rdflib.md`, piège 1.
- **`URIRef(x)` n'est pas `f<{x}>`** si un `@base` est en portée : piège 2 de
  la même page.

---

## 2 bis. Ce que le langage a gagné en 0.4.0

Quatre changements, tous implémentés et testés. Ils rendent caduques
certaines habitudes prises avant cette version.

- **`ex:{?id}` s'instancie.** La partie locale d'un nom préfixé était la
  seule position de terme où une variable ne s'instanciait pas : elle rendait
  `ex:id`, la même IRI à chaque ligne, sans erreur. Elle se résout désormais
  contre les liaisons courantes. Attention : `ex:{…}` **concatène sans
  encoder** ; c'est `e<…{?id}>` qui encode en pour-cent. Choisissez selon que
  la valeur peut contenir une espace ou une barre oblique, et dites-le en
  note. Sur une valeur ordinaire, `ex:{expr}` reste immédiat et ne demande
  aucune liaison.
- **`+{ }` et `-{ }` en suite d'instruction composée.** `if cond: +{ … }`
  sur une seule ligne est accepté. Inutile donc d'ouvrir un bloc pour un `if`
  d'une ligne — c'est précisément ce qui allongeait les traductions.
- **`b.raw`.** Sur `for @bindings as b in rows:`, `b[key]` est le terme RDF
  et `b.raw[key]` la valeur telle qu'elle est arrivée. C'est ce qu'il faut
  quand l'original teste `if row[col] != "":`, car `Literal("") != ""`.
- **Avertissement « préfixe déclaré = nom Python »** : le transpileur le
  signale désormais. S'il apparaît, c'est un vrai piège du fichier, pas un
  bruit.

Deux pièges de fidélité, vérifiés sur rdflib 7.2.1, qui ont déjà produit des
traductions fausses :

- `Literal('x')` et `Literal('x', datatype=xsd:string)` **ne sont pas
  égaux** : le premier a un `datatype` nul. Traduire `Literal(v, XSD.string)`
  par une interpolation nue `{v}` change donc le graphe. Il faut
  `{v}^^xsd:string`.
- `Literal(True, datatype=XSD.boolean)` vaut `"true"` quand `f"{True}"` vaut
  `"True"` : rdflib normalise la forme lexicale d'un littéral typé construit
  depuis une valeur Python. La réécriture mécanique n'est sûre que si la
  valeur est déjà une chaîne.

Et une subtilité de portée, à connaître avant de désigner un graphe :
**`@graph g` capture la VALEUR de `g` à sa ligne, pas le nom.** Si le code
réaffecte `g` plus loin (`g = g + autre`), il faut une nouvelle déclaration
`@graph g` après la réaffectation, sans quoi les écritures partent dans le
graphe devenu inatteignable — en silence.

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

Écrivez un **graphe d'entrée** `fixture.ttl` à côté
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

**Ce n'est pas une consigne de forme, et la campagne du 2026-08-29 l'a montré.**
Elle a écrit `nom préfixé`, `nom prefixe` et `prefixed name` pour une seule
et même construction ; `suffixe d'appel (g)` à côté de `call suffix (g)` ;
`littéral typé`, `litteral type` et `typed literal` ; `f<...>` à côté de
`f<…>`. Sept constructions apparentes là où il y en avait trois.
`constructions.normalise` les a rabattues — les comptes publiés sont
justes — mais elle ne peut rabattre que ce qu'elle a déjà vu. Écrivez les
libellés **en anglais, sans accent, tels que ci-dessus**, en copiant depuis
cette liste plutôt qu'en les retapant de mémoire.

Classification de la traduction :
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

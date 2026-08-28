# Empirical Evaluation of linked-data-python

We want to build a systematic empirical evaluation of `linked-data-python` against real-world Python code that manipulates RDF. You already have access to the project context, source code, and existing tooling. Inspect the repository first and adapt the implementation to the project's existing architecture rather than introducing unnecessary parallel infrastructure.

This will be done in folder `github` in the repository root *(renommé `corpus-study/` le 2026-08-28)*

The evaluation should ultimately support the claims in the paper: LD Python reduces the syntactic gap between Python and RDF/Turtle while remaining compatible with ordinary Python tooling and semantics.

## 1. Overall evaluation pipeline

Implement an evaluation pipeline with the following stages:

1. Discover real-world Python repositories that use RDFLib extensively.
2. Download/clone and index those repositories.
3. Extract Python files.
4. Measure how RDF-heavy each file is.
5. Select a stratified corpus of RDF-manipulating files/code regions.
6. Produce semantics-preserving LD Python counterparts.
7. Run quantitative comparisons between RDFLib Python and LD Python.
8. Record cases that cannot be translated naturally.
9. Generate machine-readable results and summary tables/figures.
10. Prepare a web-based user-study application that can later be opened to participants for an extended evaluation period.

Do not fabricate evaluation results. Build tooling that makes the experiment reproducible and allows the actual data to be collected later.

---

# 2. Corpus construction

Find a defensible set of public GitHub/PyPI projects that use RDFLib substantially.

The repository selection should not be based only on popularity. Prefer a diverse corpus containing, where possible:

* RDF libraries/tools
* semantic-web applications
* data-processing projects
* RDF conversion/import/export tools
* ontology/vocabulary-related projects
* SPARQL-heavy applications
* tests/examples that genuinely construct or manipulate RDF

Record for every repository:

* repository URL
* commit/revision used
* project name
* licence
* source of discovery
* RDF-related dependencies
* approximate project size
* number of Python files
* RDF-heavy Python files

The exact repository list should be reproducible. Store it in a version-controlled manifest rather than embedding it in scripts.

Respect repository licences and do not redistribute source code where the licence does not permit it.

---

# 3. Detect RDF-heavy Python files

Do not simply grep for strings such as `URIRef`, `Literal`, and `BNode`.

Implement an AST-based RDF usage analysis where practical.

Identify at least:

* `URIRef`
* `Literal`
* `BNode`
* `Namespace`
* `NamespaceManager`
* `Graph`
* `ConjunctiveGraph`
* `Dataset`
* `add`
* `remove`
* `triples`
* `quads`
* RDF namespace terms
* namespace-derived RDF terms
* RDF graph construction
* RDF serialization/parsing
* SPARQL query/update operations

Distinguish between actual RDF operations and incidental occurrences, e.g. an imported name that is never used.

For every Python file compute metrics including:

* total LOC
* logical LOC if readily available
* token count
* AST node count
* number of RDF-related AST nodes
* number of RDF terms constructed
* number of explicit RDFLib constructors
* number of triples/quads constructed
* number of graph operations
* RDF density

Define and document the RDF-density metric clearly.

For example, consider a normalized metric such as:

`RDF-related AST nodes / total AST nodes`

but also retain raw counts. We should be able to experiment with different thresholds later.

---

# 4. Corpus sampling

Do not select only files above one arbitrary threshold.

Create RDF-density bands, for example:

* low RDF density
* medium RDF density
* high RDF density

Use configurable thresholds rather than hard-coding them.

Retain a random sample of lower-density files as a control group.

For the intensive evaluation, prioritize high-density files, but make the exact sampling reproducible using a fixed random seed.

The final dataset should contain enough information to answer:

> Does the benefit of LD Python increase with the amount of RDF manipulation in a file?

Avoid cherry-picking particularly attractive examples.

---

# 5. Identify RDF manipulation regions

Whole Python files contain a lot of code that LD Python does not affect.

Therefore, identify RDF-heavy functions or contiguous code regions inside files where possible.

For each selected region retain:

* repository
* file
* function/class/module location
* source revision
* original source
* RDF-related metrics
* surrounding context needed to understand it
* dependencies/imports required to translate or execute it

Use whole files when function-level extraction would make the example misleading or impossible to understand.

---

# 6. Generate LD Python equivalents

For every selected example, create an equivalent LD Python representation.

The translation must preserve semantics.

Do not optimize or refactor the original program merely to make LD Python look better.

The comparison should be:

> same program / same RDF behaviour / different notation

not:

> old implementation / redesigned implementation.

Where possible, automate the mechanical parts of the conversion.

For each example classify the translation:

* directly expressible
* expressible with minor restructuring
* expressible but awkward
* not expressible
* excluded for another documented reason

Record the reason for every non-trivial translation.

---

# 7. Semantic equivalence validation

Every converted example should be validated, if possible.

Depending on the example, compare:

* test results
* generated RDF graphs
* generated triples/quads
* SPARQL query results
* serialized RDF after normalization
* observable return values

Do not compare raw serialization byte-for-byte when RDF ordering makes that inappropriate.

Build normalization/comparison helpers where necessary.

A translated example should not enter the final quantitative comparison unless its semantic equivalence has been established or it is explicitly marked as an unresolved case.

---

# 8. Quantitative comparison

For each matched RDFLib/LD Python example compute at least:

### Surface size

* lines of code
* tokens
* characters
* AST nodes
* ... (feel free to add more)

### RDF-specific complexity

* RDFLib constructor calls
* `URIRef`/`Literal`/`BNode` construction
* explicit namespace manipulation
* graph construction calls
* graph operations
* Python operations required per RDF triple
* RDF terms per line
* RDF triples per line

The main hypothesis is that LD Python reduces the amount of general-purpose Python syntax required to express RDF structures.

Do not rely on LOC alone.

Generate aggregate statistics and distributions, not only means.

For example:

* median reduction
* mean reduction
* quartiles
* percentage reduction
* distribution by RDF-density band
* distribution by repository
* distribution by RDF programming pattern

Also investigate the relationship between RDF density and LD Python benefit.

---

# 9. Important analysis: RDF/code correspondence

Add metrics that directly test the motivation of the language.

The important question is not merely:

> Is LD Python shorter?

but:

> Does LD Python make RDF structures more directly visible in the source code?

Design measurable proxies for this.

Potential metrics include:

* explicit RDF constructors per triple
* Python AST nodes per triple
* generic function/method calls per triple
* syntactic nesting required to express a triple
* tokens between RDF subject/predicate/object components
* number of intermediate Python expressions required to construct RDF terms

Document exactly how each metric is computed.

Keep these metrics modular so additional metrics can be added later.

---

# 10. Produce reproducible artifacts

Create a reproducible evaluation command, ideally along the lines of:

`evaluate corpus`

or whatever command structure fits the existing project.

It should be possible to run the evaluation in stages:

* repository acquisition
* corpus analysis
* sampling
* translation
* semantic validation
* metric extraction
* aggregate analysis
* user-study dataset generation

Avoid a monolithic script.

Store raw machine-readable data, preferably JSON/JSONL/CSV as appropriate, separately from generated summaries.

Every generated result should be traceable back to:

* repository
* commit
* file
* code region
* transformation
* evaluation version/configuration

---

# 11. User study: prepare the website now, collect participants later

Prepare a complete web application for a future user study. This will be done in folder `user_study` in the repository root.

The objective is **not to recruit or contact users now**. Build the infrastructure so that we can open the study to participants over a chosen evaluation period later.

The website should support a controlled within-subject comparison between ordinary RDFLib Python and LD Python.

## Study design

Participants should receive matched programming tasks involving RDF-manipulating code.

Possible tasks include:

* identify what RDF triples a piece of code constructs
* identify a predicate/object relationship
* determine the effect of a code fragment
* modify a program to add a specified RDF relationship
* find where a particular RDF term is introduced
* answer comprehension questions about an RDF graph-producing function

Compare performance on RDFLib and LD Python representations.

Collect:

* task correctness
* completion time
* errors/attempts where useful
* representation shown
* task identifier
* participant/session identifier
* order of conditions
* optional subjective difficulty rating
* optional RDF/Python experience questionnaire

Use a randomized/counterbalanced assignment so that participants do not always see the same representation first.

Do not show the same underlying example twice to a participant merely in a different notation unless the experiment explicitly requires that.

---

# 12. Website requirements

Build the website so that the study can be configured without changing application code.

The configuration should specify:

* study title
* introduction/consent text
* study period
* tasks
* task variants
* condition assignment
* demographic/experience questions
* post-task questions
* final questionnaire

Include a clear landing page explaining the purpose of the study at a high level.

Include an informed-consent step before participation.

Include a short participant background questionnaire, particularly:

* Python experience
* RDF experience
* RDFLib experience
* familiarity with Turtle
* approximate programming experience

Do not collect unnecessary personally identifying information.

Prefer anonymous/pseudonymous participant IDs.

Do not require an account unless there is a strong technical reason.

---

# 13. User-study experiment engine

Implement the study as an experiment engine rather than a hard-coded collection of pages.

It should support:

* randomized participant assignment
* counterbalancing
* condition tracking
* task ordering
* timed tasks
* answer validation
* Likert-style questions
* free-text feedback
* session persistence
* incomplete-session handling
* completion tracking

The experiment should be resumable if the participant accidentally refreshes the page, while avoiding duplicate submissions.

Store timestamps needed for measuring task completion time.

Do not expose the correct answers in client-side code if that would make them trivial to inspect.

---

# 14. Privacy and research-readiness

Treat this as a real human-subject study infrastructure.

Minimize collected data.

Clearly distinguish:

* anonymous experimental data
* optional contact information, if we later decide to collect it
* administrative/study metadata

Make data retention configurable.

Provide an export mechanism for anonymized study results.

Include a mechanism to delete a participant's data if required by the eventual study protocol.

Do not claim ethics/IRB approval or GDPR compliance unless the project actually has the necessary approval/legal basis. Instead, structure the application so that the eventual consent and privacy text can be supplied by the researchers.

---

# 15. Results dashboard

Prepare an internal/researcher-only results view or export pipeline.

It should eventually let us inspect:

* number of participants
* completion rate
* performance by condition
* completion time by condition
* accuracy by condition
* effect by task
* effect by participant RDF experience
* order effects
* subjective difficulty
* free-text feedback

Do not expose participant-level data publicly by default.

Prefer exporting anonymized aggregate data for statistical analysis.

---

# 16. Statistical analysis preparation

Do not hard-code statistical conclusions.

Prepare a dataset suitable for later analysis of:

* paired differences in completion time
* paired differences in accuracy
* representation effects
* task effects
* participant experience effects
* order/counterbalancing effects

Because participants will perform multiple tasks, retain the repeated-measures structure rather than collapsing everything into one participant score.

The final analysis can later use paired tests or mixed-effects models as appropriate.

---

# 17. Deliverables

At the end of this implementation, I want:

1. A reproducible repository manifest.
2. A corpus acquisition/indexing tool.
3. An AST-based RDF-density analyser.
4. A reproducible corpus sampling mechanism.
5. RDF-heavy region extraction.
6. A framework for generating and recording LD Python equivalents.
7. Semantic-equivalence validation.
8. Quantitative comparison metrics.
9. Generated CSV/JSON results.
10. Scripts for aggregate statistics and plots.
11. A prepared web-based user-study application.
12. Configurable participant/task/condition assignment.
13. Anonymous study-data storage and export.
14. Documentation explaining how to run the entire pipeline.
15. A short evaluation README explaining the methodology and assumptions.

---

# 18. Engineering constraints

Before implementing anything:

* inspect the existing project architecture;
* reuse existing dependencies and conventions where possible;
* do not introduce a large framework unnecessarily;
* keep the evaluation tooling separate from the core LD Python implementation;
* make all thresholds/configuration explicit;
* make sampling deterministic;
* make transformations reproducible;
* preserve provenance for every example;
* write tests for the corpus analysis and metric calculations;
* make failures explicit rather than silently dropping examples.

If an aspect of the methodology is ambiguous, choose the most defensible implementation, document the decision, and make it configurable rather than blocking implementation.

The goal is to leave the project with a **research-grade, reproducible evaluation pipeline plus a ready-to-deploy user-study website**, not merely a collection of hand-selected examples.

# 19. Put results in the article

Once the results are obtained, A section about the evaluation should be added to the `article/tex/main.tex` file.
Assume no page limit is imposed for the article
the article, compiled, goes to google drive of Maxime, root, name linked-data-python.pdf
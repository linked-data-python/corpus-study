"""Empirical evaluation pipeline: RDFLib Python corpus vs Linked-Data Python.

One study, drawn by **kind of use**: for each recognised way real code uses
RDFLib, is the construction the language proposes for it useful, where, and
how often?

Stages (each is a subcommand of ``python -m rdfeval``):

    discover   query GitHub / Wheelodex for candidate repositories
    select     apply inclusion criteria, write the version-controlled manifest
    acquire    clone the manifest repositories at pinned commits
    analyze    AST-based RDF-usage analysis of every Python file
    surface    shapes of the code, and the site index the draw samples from
    strata     the seeded stratified draw, and the example tree it scaffolds
    validate   establish semantic equivalence of each translated pair
    compare    pairwise quantitative metrics (surface + RDF-specific)
    review     the incremental human review, pair by pair
    aggregate  aggregate statistics, tables and figures — APPROVED pairs only
    article    publishable examples and the construction-provenance table
    status     where the campaign stands
    check      the two machine checks on one example, in order
    audit      hand-judged precision/recall audit of the analyser
    userstudy  export approved pairs as user-study task material
"""

__version__ = "0.2.0"

"""Empirical evaluation pipeline: RDFLib Python corpus vs Linked-Data Python.

Stages (each is a subcommand of ``python -m rdfeval``):

    discover   query GitHub / Wheelodex for candidate repositories
    select     apply inclusion criteria, write the version-controlled manifest
    acquire    clone the manifest repositories at pinned commits
    analyze    AST-based RDF-usage analysis of every Python file
    sample     stratified, seeded sampling of RDF-density bands
    regions    extract RDF-heavy code regions from sampled files
    translate  scaffold LD Python counterparts for extracted regions
    validate   establish semantic equivalence of each translated pair
    compare    pairwise quantitative metrics (surface + RDF-specific)
    aggregate  aggregate statistics, tables and figures
    userstudy  export validated pairs as user-study task material
"""

__version__ = "0.1.0"

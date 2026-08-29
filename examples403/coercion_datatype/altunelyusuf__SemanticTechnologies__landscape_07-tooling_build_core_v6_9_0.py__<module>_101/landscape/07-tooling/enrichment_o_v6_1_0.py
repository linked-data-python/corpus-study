#!/usr/bin/env python3
"""enrichment_o_v6_1_0.py — adds real content from a user-supplied external
source (2026-08-06 commission): the O'Reilly book "Agentic GraphRAG" by
Anthony Alcaraz and Sam Julien (August 2026), fetched in full (full table of
contents confirmed: dual-graph architecture, graph memory systems, reasoning
and planning, tool orchestration, self-evolution, optimization). One of its
named production systems, Zep's Graphiti temporal knowledge-graph memory
engine, is independently corroborated by its own arXiv paper, fetched
separately rather than taken on the book's word alone."""

EXT8 = {
 "R-AGRAG": {
  "cite": "Alcaraz, A., Julien, S. (2026). Agentic GraphRAG. O'Reilly Media.",
  "url": "https://www.oreilly.com/library/view/agentic-graphrag/9798341623163/",
  "level": "TOOLCHAIN-VERIFIED", "ev": "fetched in full 2026-08-06, full table of contents confirmed",
 },
 "R-ZEP": {
  "cite": "Rasmussen, P. et al. (2025). Zep: A Temporal Knowledge Graph Architecture for Agent Memory. arXiv:2501.13956.",
  "url": "https://arxiv.org/abs/2501.13956",
  "level": "TOOLCHAIN-VERIFIED", "ev": "fetched, abstract confirmed 2026-08-06, independently corroborates Graphiti",
 },
}
MARKER8 = {"Alcaraz & Julien, 2026": "R-AGRAG", "Rasmussen et al., 2025": "R-ZEP"}

# (id, label, kind, home_class, defn, refs)
NEW_INSTANCES = [
 ("AgenticGraphMemorySystem", "Agentic graph memory system", "Concept", "T3C4",
  "An agentic graph memory system represents an AI agent's memory as a graph rather than a flat vector index, "
  "typically pairing a vertical knowledge graph of domain facts with a horizontal workflow graph of the agent's "
  "own actions, so retrieval, planning and self-evaluation can all query the same structure (Alcaraz and "
  "Julien, 2026).",
  ["R-AGRAG"]),
 ("GraphitiMemoryFramework", "Graphiti", "Library", "T3C4",
  "Graphiti is Zep's open-source temporally-aware knowledge-graph engine for agent memory: every edge carries "
  "explicit validity intervals, so a new fact invalidates rather than deletes an old one, preserving a queryable "
  "history while the agent reasons over current state; it outperformed the prior state-of-the-art system MemGPT "
  "on the Deep Memory Retrieval benchmark (Rasmussen et al., 2025; Alcaraz and Julien, 2026).",
  ["R-ZEP", "R-AGRAG"]),
]

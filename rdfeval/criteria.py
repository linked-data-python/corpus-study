"""Repository inclusion criteria, in two stages.

Stage 1 (:func:`stage1_reasons`) decides from GitHub metadata alone — no clone
needed. Stage 2 (:func:`stage2_reason`) decides from the analysis of the clone.
Both return the *reasons for rejection*, never a bare boolean, so that every
excluded repository can say why it is out (`manifest/excluded.jsonl`, or the
``pruned`` field of a manifest record).

The thresholds live in ``[selection]`` of ``config/evaluation.toml``; this
module holds no constant of its own. The criteria are option B7 of
``options_repo_selection.md``, retained on 2026-08-28 and documented in
``funnel.md`` §6.

A record here is the merge of a discovery entry (which channels found it) and
a ``manifest/repo_stats.jsonl`` entry (GitHub metadata). Missing metadata is
treated as *unknown*, and unknown never satisfies a criterion: a repository
whose licence could not be read is rejected by ``require_snippet_licence``
rather than silently admitted.
"""

from __future__ import annotations

import re


def _text(rec: dict) -> str:
    """Full name, description and topics, lowercased — where markers are sought."""
    return " ".join([
        rec.get("full_name", ""),
        rec.get("description") or "",
        " ".join(rec.get("topics") or []),
    ]).lower()


def python_bytes(rec: dict) -> int:
    return (rec.get("languages") or {}).get("Python", 0)


def is_teaching(rec: dict, markers) -> bool:
    """Does a teaching marker start a word of the name/description/topics?

    Substring matching is too crude — ``course`` is inside ``discourse``. A
    marker must begin a word (be preceded by something that is not a letter),
    but need not end one: ``Curso2025-2026`` and ``coursework`` both count.
    """
    text = _text(rec)
    return any(re.search(r"(?<![^\W\d_])" + re.escape(m), text) for m in markers)


def is_library_clone(rec: dict, names) -> bool:
    full = rec.get("full_name", "")
    if "/" not in full:
        return False
    return full.split("/", 1)[1].lower() in {n.lower() for n in names}


def stage1_reasons(rec: dict, cfg: dict) -> list[str]:
    """Why this candidate cannot enter the corpus, from metadata alone.

    An empty list means the repository is selectable.
    """
    out: list[str] = []
    if rec.get("unavailable"):
        out.append("unavailable")
    if rec.get("empty"):
        out.append("empty")
    if cfg["exclude_forks"] and rec.get("fork"):
        out.append("fork")
    if cfg["exclude_archived"] and rec.get("archived"):
        out.append("archived")
    if cfg.get("exclude_mirrors") and (rec.get("mirror") or rec.get("template")):
        out.append("mirror_or_template")
    if python_bytes(rec) < cfg["min_python_bytes"]:
        out.append(f"python_bytes<{cfg['min_python_bytes']}")
    if (rec.get("commits") or 0) < cfg["min_commits"]:
        out.append(f"commits<{cfg['min_commits']}")
    size = rec.get("size_kb")
    if size is None or size < cfg["min_size_kb"]:
        out.append(f"size<{cfg['min_size_kb']}kb")
    elif size > cfg["max_size_kb"]:
        out.append(f"size>{cfg['max_size_kb']}kb")
    if (rec.get("last_commit") or "")[:10] < cfg["min_last_commit"]:
        out.append(f"inactive_since<{cfg['min_last_commit']}")
    if cfg.get("require_snippet_licence") and \
            (rec.get("licence") or "") not in set(cfg["snippet_licences"]):
        out.append(f"licence={rec.get('licence') or 'none'}")
    if cfg.get("exclude_teaching") and is_teaching(rec, cfg["teaching_markers"]):
        out.append("teaching_material")
    if cfg.get("exclude_library_clones") and \
            is_library_clone(rec, cfg["library_clone_names"]):
        out.append("library_itself")
    return out


def stage2_reason(rec: dict, cfg: dict) -> str | None:
    """Why an analysed repository should be pruned, or None to keep it.

    ``rec`` is a manifest entry after ``rdfeval analyze`` filled in
    ``python_files``, ``rdf_files`` and ``analysis_errors``.
    """
    n_py = rec.get("python_files")
    if n_py is None:
        return None                      # not analysed yet: no verdict
    if n_py < cfg["min_python_files"]:
        return f"python_files={n_py}<{cfg['min_python_files']}"
    if n_py and rec.get("analysis_errors", 0) >= n_py:
        return "all_files_unparsable"    # Python 2 project
    if (rec.get("rdf_files") or 0) < cfg["min_rdf_files"]:
        return f"rdf_files=0<{cfg['min_rdf_files']}"
    return None


def is_vendored(rel_parts: tuple[str, ...], repo_name: str, cfg: dict) -> bool:
    """Is this path inside a third-party library copied into the repository?

    ``rel_parts`` is the path relative to the checkout root. A top-level
    directory named after a known library is vendored *unless it is the
    repository's own package* — ``RDFLib/sparqlwrapper`` keeps its
    ``SPARQLWrapper/`` tree, which is its own source.

    The ``vendored_dirs_always`` markers (``_vendor``, ``vendor``,
    ``third_party``…) match at **any depth**: they are never a project's own
    package, and a copy of rdflib buried under one is still rdflib.  Matching
    only the top level let two such copies reach the draw —
    ``globalPlugins/contextLabeler/_vendor/rdflib/collection.py`` and
    ``bindings/python/tests/rdflib_suite/vendor/test_having.py`` — where they
    were caught by hand, as *the library's own implementation* rather than
    code written against it.
    """
    if not rel_parts:
        return False
    # A `.../lib/python*/…` tree is a bundled runtime: the layout of a
    # virtualenv without the `site-packages` marker that `exclude_dirs`
    # recognises (seen in `prrvchr/mContactOOo`, which ships setuptools,
    # selenium and trio under `uno/lib/python/`).
    lowered = [p.lower() for p in rel_parts]
    for a, b in zip(lowered, lowered[1:]):
        if a == "lib" and b.startswith("python"):
            return True
    always = {d.lower() for d in cfg.get("vendored_dirs_always", [])}
    if always.intersection(lowered):
        return True
    top = lowered[0]
    if top in {d.lower() for d in cfg.get("vendored_dirs", [])}:
        own = repo_name.split("/")[-1].lower().replace("-", "").replace("_", "")
        return top.replace("-", "").replace("_", "") != own
    return False

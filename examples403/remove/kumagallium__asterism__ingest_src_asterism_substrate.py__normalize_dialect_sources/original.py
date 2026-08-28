# Extracted from kumagallium/asterism@f0977d4d3a : ingest/src/asterism/substrate.py
# region: normalize_dialect_sources (lines 243-339, stratum remove)
# licence of the source repository: see meta.json
from dataclasses import dataclass, replace
from pathlib import Path
from asterism.dialect import (
    DEFAULT_DIALECT,
    ENCODING_ATTEMPTS,
    LEGACY_SUFFIXES,
    DialectAnnotationError,
    dialects_from_mapping,
    encoding_that_decodes,
    is_default,
    normalize_source,
    strip_dialect_annotations,
)
from asterism.rml_validate import RmlValidationError as RmlValidationError
logger = logging.getLogger(__name__)

def normalize_dialect_sources(rml_ttl: str, csv_dir: Path | str, work_dir: Path | str) -> str:
    """Normalize every ``ast:``-annotated source to a UTF-8 comma CSV work-dir copy,
    rewriting its ``rml:source`` to the copy's absolute path and stripping the
    annotation triples. The EXTENSION decides too: a legacy-suffix source
    (``.txt``/``.dat``/``.asc`` — Morph-KGC cannot resolve its source type at
    all) is normalized under the default dialect even when nothing is
    annotated. A mapping with no annotations and no legacy-suffix source is
    returned **byte-identical** (the all-defaults gate: absence of dialect ⇒
    current behavior). An annotated source absent on disk is left for
    :func:`asterism.rml_validate.validate_rml_design` to report (its
    missing-source message is the actionable one). An out-of-contract
    annotation value raises the structured :class:`RmlValidationError` (422).
    Runs FIRST in the work-dir chain, so the later steps see the normalized
    copy as an absolute (already resolved) source and skip it.
    """
    import rdflib

    graph = rdflib.Graph()
    try:
        graph.parse(data=rml_ttl, format="turtle")
    except Exception:
        return rml_ttl  # rml_safety owns the parse-error rejection
    try:
        dialects = dialects_from_mapping(graph)
    except DialectAnnotationError as exc:
        raise RmlValidationError([str(exc)]) from exc
    for pred in ("http://w3id.org/rml/source", "http://semweb.mmlab.be/ns/rml#source"):
        for src in graph.objects(None, rdflib.URIRef(pred)):
            path = Path(str(src))
            if path.suffix.lower() in LEGACY_SUFFIXES and not path.is_absolute():
                dialects.setdefault(path.name, DEFAULT_DIALECT)
    if not dialects:
        return rml_ttl
    base = Path(csv_dir)
    work = Path(work_dir)
    work.mkdir(parents=True, exist_ok=True)
    normalized: dict[str, Path] = {}
    for name, dialect in dialects.items():
        src = base / name
        # is_default gate: an annotation set that resolves to all-defaults means
        # "read as today" — strip it below, but never rewrite the source. A
        # legacy suffix is the exception: Morph-KGC cannot read it at all, so
        # the default-dialect normalization to .csv still runs.
        if not src.exists():
            continue
        if is_default(dialect) and Path(name).suffix.lower() not in LEGACY_SUFFIXES:
            continue
        # Keep the basename recognizable; a non-.csv name gets ".csv" appended so
        # downstream header checks treat the copy as the tabular file it now is.
        dest = work / (name if name.lower().endswith(".csv") else name + ".csv")
        try:
            normalized[name] = normalize_source(src, dialect, dest)
        except UnicodeDecodeError as exc:
            # The pinned encoding does not decode the file. Which encoding reads a
            # file is a question the machine can answer, so it answers it instead of
            # sending the person away to convert the file by hand: try the pinned
            # codecs in order and re-run the normalization with the one that works.
            # Only the ENCODING is repaired — the delimiter, the header offset and the
            # preamble mode are design decisions, and they plainly worked (live
            # 2026-08-26: an XRD export detected as cp932 at every design stage, pinned
            # as utf-8-sig, refused here).
            repaired = encoding_that_decodes(src, dialect.encoding)
            if repaired is None or repaired == dialect.encoding:
                raise RmlValidationError(
                    [
                        f"source file {name!r} cannot be decoded with its pinned "
                        f"dialect encoding {dialect.encoding!r}: {exc}. No known text "
                        f"encoding reads it either (tried "
                        f"{', '.join(ENCODING_ATTEMPTS)}) — the file may be binary, "
                        "truncated, or saved in an encoding this reader does not carry."
                    ]
                ) from exc
            logger.warning(
                "source %r does not decode as its pinned %r; reading it as %r instead "
                "(the design's pin is stale — re-designing re-pins it)",
                name,
                dialect.encoding,
                repaired,
            )
            dialect = replace(dialect, encoding=repaired)
            try:
                normalized[name] = normalize_source(src, dialect, dest)
            except UnicodeDecodeError as exc2:  # pragma: no cover — defensive
                raise RmlValidationError(
                    [
                        f"source file {name!r} cannot be decoded with its pinned "
                        f"dialect encoding {dialect.encoding!r}: {exc2}."
                    ]
                ) from exc2
    for pred in ("http://w3id.org/rml/source", "http://semweb.mmlab.be/ns/rml#source"):
        for s, o in list(graph.subject_objects(rdflib.URIRef(pred))):
            dest = normalized.get(Path(str(o)).name)
            if dest is not None:
                graph.remove((s, rdflib.URIRef(pred), o))
                graph.add((s, rdflib.URIRef(pred), rdflib.Literal(str(dest))))
    strip_dialect_annotations(graph)
    return graph.serialize(format="turtle")

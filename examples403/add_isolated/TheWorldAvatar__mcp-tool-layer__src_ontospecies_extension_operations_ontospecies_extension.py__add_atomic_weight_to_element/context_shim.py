# Context shim (see meta.json), for TheWorldAvatar/mcp-tool-layer@c440a33e08 :
# src/ontospecies_extension/operations/ontospecies_extension.py.
#
# OS, _class, _mint_hash_iri, _ensure_type_with_label, _safe_parent and
# locked_graph are module-level constants/helpers add_atomic_weight_to_element
# (lines 566-587 of the source file) calls, but that are defined elsewhere in
# the same file: OS line 15; _class lines 55-56; _mint_hash_iri lines 58-61;
# _ensure_type_with_label lines 203-206; _safe_parent lines 208-209;
# locked_graph lines 181-201 (plus _memory_paths, lines 171-179, and
# _sanitize_label, lines 104-148, that it/its callee needs). OS, _class,
# _ensure_type_with_label, _safe_parent and _sanitize_label are copied
# verbatim.
#
# _mint_hash_iri is made deterministic. The real implementation hashes
# datetime.now(timezone.utc) (line 59), so calling it once from original.py
# and once from translated.ldpy -- two separate calls, necessarily at
# different wall-clock instants -- would mint two different IRIs for `aw`,
# and the isomorphism oracle would report a difference that is about the
# clock, not the translation. Both sides call this identical, fixed-output
# stand-in instead.
#
# locked_graph is simplified to `yield Graph()`: the real implementation
# acquires a FileLock and parses/serialises a TTL file under
# data/<hash>/memory_ontospecies/ -- filesystem locking and persistence that
# add_atomic_weight_to_element's own body never inspects (it only reads/
# writes the yielded `g` inside the `with` block, which is exactly what
# driver.py compares) and that would need the `filelock` package plus a
# writable data directory -- an external dependency out of reach here and
# out of scope for this region. See driver.py for how the yielded graph
# (otherwise invisible: it is never returned, and it is not a parameter
# either) is made observable to the pilot.
import re
import unicodedata
from contextlib import contextmanager
from typing import Optional
from urllib.parse import urlparse

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

OS = Namespace("http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#")
INST_BASE = "https://www.theworldavatar.com/kg/OntoSpecies/instance"


def _class(ns: Namespace, local: str) -> URIRef:
    return getattr(ns, local)


def _mint_hash_iri(class_local: str) -> URIRef:
    return URIRef(f"{INST_BASE}/{class_local}/deterministic-test-hash")


def _sanitize_label(raw_label: str) -> str:
    """Sanitize labels to ensure proper Greek character representation."""
    if raw_label is None:
        return "entity"
    label = str(raw_label)
    label = unicodedata.normalize("NFKC", label)
    cleaned_chars = []
    for ch in label:
        cat = unicodedata.category(ch)
        if cat.startswith("C"):
            continue
        if ch.isspace():
            cleaned_chars.append(" ")
        else:
            cleaned_chars.append(ch)
    label = "".join(cleaned_chars)
    single_letter_greek = {
        "a": "α", "b": "β", "g": "γ", "d": "δ", "e": "ε",
        "z": "ζ", "h": "η", "q": "θ", "i": "ι", "k": "κ",
        "l": "λ", "m": "μ", "n": "ν", "x": "ξ", "o": "ο",
        "p": "π", "r": "ρ", "s": "σ", "t": "τ", "u": "υ",
        "f": "φ", "c": "χ", "y": "ψ", "w": "ω",
    }
    for letter, greek_char in single_letter_greek.items():
        label = re.sub(r"([-_])%s\b" % re.escape(letter), r"\1%s" % greek_char, label)
    label = re.sub(r"\s+", " ", label).strip()
    return label or "entity"


def _ensure_type_with_label(g: Graph, iri: URIRef, cls: URIRef, label: Optional[str] = None) -> None:
    g.add((iri, RDF.type, cls))
    if label is not None:
        g.set((iri, RDFS.label, Literal(_sanitize_label(label))))


def _is_abs_iri(s: str) -> bool:
    try:
        u = urlparse(s)
        return bool(u.scheme) and bool(u.netloc)
    except Exception:
        return False


def _safe_parent(parent_iri: str) -> Optional[URIRef]:
    return URIRef(parent_iri) if _is_abs_iri(parent_iri) else None


# Set by driver.py right before each call, and read by locked_graph() when
# add_atomic_weight_to_element opens its `with` block -- see driver.py for
# why this needs careful, non-overlapping sequencing between the two sides.
LAST_GRAPH = None


@contextmanager
def locked_graph(timeout: float = 30.0):
    global LAST_GRAPH
    g = Graph()
    LAST_GRAPH = g
    yield g

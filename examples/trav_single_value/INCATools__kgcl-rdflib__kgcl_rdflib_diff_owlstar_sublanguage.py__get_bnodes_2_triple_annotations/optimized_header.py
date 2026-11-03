# Extracted from INCATools/kgcl-rdflib@7af638bbd7 : kgcl_rdflib/diff/owlstar_sublanguage.py
# region: get_bnodes_2_triple_annotations (lines 303-343, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import BNode
from rdflib.namespace import OWL

def get_bnodes_2_triple_annotations(g):
    """Get blank nodes to triple annotations."""
    predicates = (OWL.annotatedSource, OWL.annotatedProperty, OWL.annotatedTarget)

    # get blank nodes that have all three required predicates
    intersection = set.intersection(*(set(g.subjects(predicate)) for predicate in predicates))

    exclude = {
        *predicates,
        # RDF.type,
    }

    annotations = {}
    for i in intersection:
        annotations[i] = []
        if isinstance(i, BNode):  # this check should be unnecessary
            # NB these generators are singletons
            annotations[i] += [(i, p, next(g.objects(i, p))) for p in predicates]
            if not any(isinstance(o, BNode) for _, _, o in annotations[i]):
                annotations[i] += [
                    (s, p, o) for s, p, o in g.triples((i, None, None))
                    if p not in exclude and not isinstance(o, BNode) and not isinstance(p, BNode)
                ]

    return annotations


# Test harness only (see meta.json): rdflib mints a FRESH internal id for
# every blank node on every parse (verified by hand -- even an explicitly
# labelled `_:ann1` does not keep that label across two independent
# parses of the same file), so `annotations`, keyed by BNode for every
# non-decoy entry, can never compare equal by plain dict equality between
# the two sides' independently-parsed fixture graphs -- run_pair's
# normalise() canonicalises a bare BNode VALUE but not a BNode used as a
# DICT KEY. `demo` repackages the result as a sorted, bnode-identity-free
# structure before handing it to run_pair, identically on both sides --
# the same kind of test-harness repackaging as `demo` in
# examples/trav_one_step/INM-6__alpaca__.../test_provenance_annotation_multiple_returns
# (there: assertions -> a comparable string; here: a bnode-keyed dict -> a
# comparable, order-independent list).
def _term_key(t):
    return ("bnode",) if isinstance(t, BNode) else ("term", repr(t))


# The SUBJECT of each collected triple is kept too (repair 2026-10-30): it
# is the dict key itself on every line the region writes, and a BNode has
# no identity across the two parses, so it is recorded relative to the key
# ("self") -- anything else (None, another node) shows as itself.
def _subject_key(s, key):
    return ("self",) if s == key else _term_key(s)


def demo(g) -> object:
    annotations = get_bnodes_2_triple_annotations(g)
    entries = []
    for key, triples in annotations.items():
        key_entry = ("bnode",) if isinstance(key, BNode) else ("named", str(key))
        triple_entries = sorted(
            (_subject_key(s, key), _term_key(p), _term_key(o)) for (s, p, o) in triples
        )
        entries.append((key_entry, triple_entries))
    return sorted(entries, key=repr)

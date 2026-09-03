# Extracted from INCATools/kgcl-rdflib@7af638bbd7 : kgcl_rdflib/diff/owlstar_sublanguage.py
# region: get_bnodes_2_triple_annotations (lines 303-343, stratum trav_single_value)
# licence of the source repository: see meta.json
from rdflib import BNode
from rdflib.namespace import OWL, RDF, RDFS

def get_bnodes_2_triple_annotations(g):
    """Get blank nodes to triple annotations."""
    source = set(g.subjects(predicate=OWL.annotatedSource))
    property = set(g.subjects(predicate=OWL.annotatedProperty))
    target = set(g.subjects(predicate=OWL.annotatedTarget))

    # get blank nodes that have all three required predicates
    intersection = source & property & target

    exclude = {
        OWL.annotatedSource,
        OWL.annotatedProperty,
        OWL.annotatedTarget,
        # RDF.type,
    }

    annotations = {}
    for i in intersection:
        annotations[i] = []
        if isinstance(i, BNode):  # this check should be unnecessary
            # NB these generators are singletons
            source = next(g.objects(subject=i, predicate=OWL.annotatedSource))
            property = next(g.objects(subject=i, predicate=OWL.annotatedProperty))
            target = next(g.objects(subject=i, predicate=OWL.annotatedTarget))

            annotations[i].append((i, OWL.annotatedSource, source))
            annotations[i].append((i, OWL.annotatedProperty, property))
            annotations[i].append((i, OWL.annotatedTarget, target))

            for s, p, o in g.triples((i, None, None)):
                if (
                    p not in exclude
                    and not isinstance(o, BNode)
                    and not isinstance(p, BNode)
                    and not isinstance(source, BNode)
                    and not isinstance(property, BNode)
                    and not isinstance(target, BNode)
                ):
                    annotations[i].append((s, p, o))

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


def demo(g) -> object:
    annotations = get_bnodes_2_triple_annotations(g)
    entries = []
    for key, triples in annotations.items():
        key_entry = ("bnode",) if isinstance(key, BNode) else ("named", str(key))
        triple_entries = sorted(
            (_term_key(p), _term_key(o)) for (_, p, o) in triples
        )
        entries.append((key_entry, triple_entries))
    return sorted(entries, key=repr)

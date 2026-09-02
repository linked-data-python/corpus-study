# Context shim (see meta.json): `in_stable_order`, transcribed verbatim from
# IndustryFusion/DigitalTwin@3b40088b88 : semantic-model/shacl2flink/lib/utils.py,
# so `import lib.utils as utils` in original.py resolves without the rest of
# the shacl2flink package (which this region does not otherwise touch).
# Identical for both representations -- this is not part of the translation.


def in_stable_order(rows):
    """
    Sort query results or graph triples into a canonical order.

    Neither SPARQL nor an rdflib graph defines an iteration order, and Python
    randomises string hashing per process, so the same shapes compiled twice
    yield the same rows in a different sequence. Everything downstream inherits
    that: row order in the generated SQL, and -- because ids are handed out as
    rows arrive -- which constraint gets which id.

    Sorting on the stringified bindings makes a build a function of its inputs
    alone.
    """
    return sorted(rows, key=lambda row: tuple(str(value) for value in row))

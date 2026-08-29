# Extracted from RDFLib/rdflib-leveldb@a0f3386c71 : test/test_store_performance2.py
# region: StoreTestCase.testNamedGraphUpdate (lines 247-359, stratum sparql_literal)
# licence of the source repository: see meta.json
import re
from time import time
from rdflib import ConjunctiveGraph, URIRef
log = logging.getLogger(__name__)
michel = URIRef("urn:michel")
bob = URIRef("urn:bob")
likes = URIRef("urn:likes")
hates = URIRef("urn:hates")
pizza = URIRef("urn:pizza")
graphuri = URIRef("urn:graph")

def testNamedGraphUpdate(self):
    t0 = time()
    g = self.graph.get_context(graphuri)
    r1 = "INSERT DATA { <urn:michel> <urn:likes> <urn:pizza> }"
    g.update(r1)
    self.assertEqual(
        set(g.triples((None, None, None))),
        set([(michel, likes, pizza)]),
        "only michel likes pizza",
    )

    r2 = (
        "DELETE { <urn:michel> <urn:likes> <urn:pizza> } "
        + "INSERT { <urn:bob> <urn:likes> <urn:pizza> } WHERE {}"
    )
    g.update(r2)
    self.assertEqual(
        set(g.triples((None, None, None))),
        set([(bob, likes, pizza)]),
        "only bob likes pizza",
    )
    says = URIRef("urn:says")

    # Strings with unbalanced curly braces
    tricky_strs = [
        "With an unbalanced curly brace %s " % brace
        for brace in ["{", "}"]
    ]
    for tricky_str in tricky_strs:
        r3 = (
            """INSERT { ?b <urn:says> "%s" }
        WHERE { ?b <urn:likes> <urn:pizza>} """
            % tricky_str
        )
        g.update(r3)

    values = set()
    for v in g.objects(bob, says):
        values.add(str(v))
    self.assertEqual(values, set(tricky_strs))

    # Complicated Strings
    r4strings = []
    r4strings.append(r'''"1: adfk { ' \\\" \" { "''')
    r4strings.append(r'''"2: adfk } <foo> #éï \\"''')

    r4strings.append(r"""'3: adfk { " \\\' \' { '""")
    r4strings.append(r"""'4: adfk } <foo> #éï \\'""")

    r4strings.append(r'''"""5: adfk { ' \\\" \" { """''')
    r4strings.append(r'''"""6: adfk } <foo> #éï \\"""''')
    r4strings.append('"""7: ad adsfj \n { \n sadfj"""')

    r4strings.append(r"""'''8: adfk { " \\\' \' { '''""")
    r4strings.append(r"""'''9: adfk } <foo> #éï \\'''""")
    r4strings.append("'''10: ad adsfj \n { \n sadfj'''")

    r4 = "\n".join(
        [
            "INSERT DATA { <urn:michel> <urn:says> %s } ;" % s
            for s in r4strings
        ]
    )
    g.update(r4)
    values = set()
    for v in g.objects(michel, says):
        values.add(str(v))
    self.assertEqual(
        values,
        set(
            [
                re.sub(
                    r"\\(.)",
                    r"\1",
                    re.sub(
                        r"^'''|'''$|^'|'$|" + r'^"""|"""$|^"|"$', r"", s
                    ),
                )
                for s in r4strings
            ]
        ),
    )

    # IRI Containing ' or #
    # The fragment identifier must not be misinterpreted as a comment
    # (commenting out the end of the block).
    # The ' must not be interpreted as the start of a string, causing the }
    # in the literal to be identified as the end of the block.
    r5 = """INSERT DATA { <urn:michel> <urn:hates> <urn:foo'bar?baz;a=1&b=2#fragment>, "'}" }"""

    g.update(r5)
    values = set()
    for v in g.objects(michel, hates):
        values.add(str(v))
    self.assertEqual(
        values, set(["urn:foo'bar?baz;a=1&b=2#fragment", "'}"])
    )

    # Comments
    r6 = """
        INSERT DATA {
            <urn:bob> <urn:hates> <urn:bob> . # No closing brace: }
            <urn:bob> <urn:hates> <urn:michel>.
        }
    #Final { } comment"""

    g.update(r6)
    values = set()
    for v in g.objects(bob, hates):
        values.add(v)
    self.assertEqual(values, set([bob, michel]))
    t1 = time()
    log.debug(f"testNamedGraphUpdate {self.store}: {t1 - t0:.5f}")

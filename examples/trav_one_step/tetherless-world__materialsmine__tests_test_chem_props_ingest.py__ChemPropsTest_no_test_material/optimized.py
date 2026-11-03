# Extracted from tetherless-world/materialsmine@0be55da099 : tests/test_chem_props_ingest.py
# region: ChemPropsTest.no_test_material (lines 42-149, stratum trav_one_step)
# licence of the source repository: see meta.json
#
# Test harness only (see meta.json): ChemPropsTest.no_test_material is a
# unittest.TestCase method that only asserts and returns None, and it needs
# `self.app.db` and `self.assertCountEqual`.  driver.py supplies a real
# unittest.TestCase instance whose `app.db` is a graph that records what is
# read from it.  `demo` (identical on both sides) turns a failed assertion
# into a comparable value and returns what the graph recorded, because the
# region itself discards what `objects()` reads (`list.sort()` returns None).
import rdflib

def no_test_material(self):
    # Initialize Expected Materials
    expected_materials = [
        # Poly(ether ether ketone)
        {
            "id": rdflib.Literal("O(C1=CC=C(C=C1)C(=O)C2=CC=C(OC3=CC=C(C=C3)[*])C=C2)[*]"),
            "stdname": rdflib.Literal("Poly(ether ether ketone)"),
            "density": rdflib.Literal(1.29),
            "abbrev": [rdflib.Literal("PEEK")],
            "altname": [rdflib.Literal("Zeniva"), rdflib.Literal("KetaSpire")],
        },
        # Polystyrene
        {
            "id": rdflib.Literal("C(C(C1=CC=CC=C1)[*])[*]"),
            "stdname": rdflib.Literal("Polystyrene"),
            "density": rdflib.Literal(1.04),
            "abbrev": [rdflib.Literal("PS")],
            "altname": list(map(rdflib.Literal, [
                "Pelaspan", "Afcolene", "Aim", "Amoco", "Bextrene", "Carinex", "Distrene", "Dylene",
                "Edistir", "Erinoid", "Fina", "Fostarene", "Gedex", "Hostyren", "Huntsman PS",
                "Lacqrene", "Ladene", "Lorkalene", "Luron", "Lustran", "Lustrex", "Neste PS",
                "Polystyrol", "Restirolo", "Sicostyrol", "Sternite", "Stiroplasto", "Stymer",
                "Styrodur", "Styron", "Styvarene", "Vestyron", "Polystyrol", "Polyzote",
                "Pyrochek 68", "polyphenylethene", "poly-1-phenylethylene", "polyvinylbenzene",
            ])),
        },
        # Nylon
        {
            "id": rdflib.Literal("N(CCCCCC(=O)[*])[*]"),
            "stdname": rdflib.Literal("Nylon 6"),
            "density": rdflib.Literal(1.08),
            "abbrev": [rdflib.Literal("PA 6"), rdflib.Literal("Nylon 6")],
            "altname": list(map(rdflib.Literal, [
                "Perlon", "Plaskon", "Poly(caprolactam)", "polyamide 6", "poly(ω-aminocaproamide)",
                "poly(6-aminocaproic acid)", "poly(ε-aminocaproic acid)", "poly(ω-caproamide)",
                "polycaprolactam", "poly-[imino-(1-oxohexamethylene)]",
            ])),
        },
    ]

    for mat in expected_materials:
        mat["abbrev"] = mat["abbrev"].sort()
        mat["altname"] = mat["altname"].sort()

    # Query the graph for the materials
    # Get everything but the alt names and abbreviations

    props = self.app.db.query(
        '''
        SELECT ?chem ?id ?stdname ?abbrev ?density
        WHERE
        {
            ?chem a <http://semanticscience.org/resource/ChemicalSubstance> .
            ?chem <http://purl.org/dc/terms/identifier> ?id .
            ?chem <http://semanticscience.org/resource/hasAttribute> ?den .
            ?den <http://semanticscience.org/resource/hasValue> ?density .
            ?chem <http://www.w3.org/2000/01/rdf-schema#label> ?stdname .
        }
        '''
    )
    materials = [
        {"id": chem_id, "stdname": stdname, "density": density,
         "altname": list(self.app.db.objects(chem, rdflib.SKOS.altLabel)).sort(),
         "abbrev": list(self.app.db.objects(chem, rdflib.SKOS.notation)).sort()}
        for chem, chem_id, stdname, abbrev, density in props
    ]
    self.assertCountEqual(expected_materials, materials)


def demo(self) -> object:
    try:
        no_test_material(self)
        outcome = "ok"
    except AssertionError as e:
        outcome = ("assertion-failed", str(e))
    return (outcome, sorted(self.app.db.reads, key=repr))

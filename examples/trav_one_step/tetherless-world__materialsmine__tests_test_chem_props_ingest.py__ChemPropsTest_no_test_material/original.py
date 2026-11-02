# Extracted from tetherless-world/materialsmine@0be55da099 : tests/test_chem_props_ingest.py
# region: ChemPropsTest.no_test_material (lines 42-149, stratum trav_one_step)
# licence of the source repository: see meta.json
import rdflib

def no_test_material(self):
    expected_materials = list()

    # Initialize Expected Materials
    # Poly(ether ether ketone)
    expected_materials.append(dict())
    mat_num = 0
    expected_materials[mat_num]["id"] = rdflib.Literal("O(C1=CC=C(C=C1)C(=O)C2=CC=C(OC3=CC=C(C=C3)[*])C=C2)[*]")
    expected_materials[mat_num]["stdname"] = rdflib.Literal("Poly(ether ether ketone)")
    expected_materials[mat_num]["density"] = rdflib.Literal(1.29)
    expected_materials[mat_num]["abbrev"] = [rdflib.Literal("PEEK")]
    expected_materials[mat_num]["altname"] = [rdflib.Literal("Zeniva"), rdflib.Literal("KetaSpire")]

    # Polystyrene
    expected_materials.append(dict())
    mat_num += 1
    expected_materials[mat_num]["id"] = rdflib.Literal("C(C(C1=CC=CC=C1)[*])[*]")
    expected_materials[mat_num]["stdname"] = rdflib.Literal("Polystyrene")
    expected_materials[mat_num]["density"] = rdflib.Literal(1.04)
    expected_materials[mat_num]["abbrev"] = [rdflib.Literal("PS")]
    expected_materials[mat_num]["altname"] = [
        rdflib.Literal("Pelaspan"),
        rdflib.Literal("Afcolene"),
        rdflib.Literal("Aim"),
        rdflib.Literal("Amoco"),
        rdflib.Literal("Bextrene"),
        rdflib.Literal("Carinex"),
        rdflib.Literal("Distrene"),
        rdflib.Literal("Dylene"),
        rdflib.Literal("Edistir"),
        rdflib.Literal("Erinoid"),
        rdflib.Literal("Fina"),
        rdflib.Literal("Fostarene"),
        rdflib.Literal("Gedex"),
        rdflib.Literal("Hostyren"),
        rdflib.Literal("Huntsman PS"),
        rdflib.Literal("Lacqrene"),
        rdflib.Literal("Ladene"),
        rdflib.Literal("Lorkalene"),
        rdflib.Literal("Luron"),
        rdflib.Literal("Lustran"),
        rdflib.Literal("Lustrex"),
        rdflib.Literal("Neste PS"),
        rdflib.Literal("Polystyrol"),
        rdflib.Literal("Restirolo"),
        rdflib.Literal("Sicostyrol"),
        rdflib.Literal("Sternite"),
        rdflib.Literal("Stiroplasto"),
        rdflib.Literal("Stymer"),
        rdflib.Literal("Styrodur"),
        rdflib.Literal("Styron"),
        rdflib.Literal("Styvarene"),
        rdflib.Literal("Vestyron"),
        rdflib.Literal("Polystyrol"),
        rdflib.Literal("Polyzote"),
        rdflib.Literal("Pyrochek 68")
    ]
    expected_materials[mat_num]["altname"] += [
        rdflib.Literal("polyphenylethene"),
        rdflib.Literal("poly-1-phenylethylene"),
        rdflib.Literal("polyvinylbenzene")
    ]

    # Nylon
    expected_materials.append(dict())
    mat_num += 1
    expected_materials[mat_num]["id"] = rdflib.Literal("N(CCCCCC(=O)[*])[*]")
    expected_materials[mat_num]["stdname"] = rdflib.Literal("Nylon 6")
    expected_materials[mat_num]["density"] = rdflib.Literal(1.08)
    expected_materials[mat_num]["abbrev"] = [rdflib.Literal("PA 6"), rdflib.Literal("Nylon 6")]
    expected_materials[mat_num]["altname"] = [rdflib.Literal("Perlon"), rdflib.Literal("Plaskon")]
    expected_materials[mat_num]["altname"] += [
        rdflib.Literal("Poly(caprolactam)"),
        rdflib.Literal("polyamide 6"),
        rdflib.Literal("poly(ω-aminocaproamide)"),
        rdflib.Literal("poly(6-aminocaproic acid)"),
        rdflib.Literal("poly(ε-aminocaproic acid)"),
        rdflib.Literal("poly(ω-caproamide)"),
        rdflib.Literal("polycaprolactam"),
        rdflib.Literal("poly-[imino-(1-oxohexamethylene)]")
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
    materials = [{"chem": chem, "id": chem_id, "stdname": stdname, "density": density} for chem, chem_id, stdname, abbrev, density in props]
    for chem in materials:
        chem["altname"] = [name for name in self.app.db.objects(chem["chem"], rdflib.URIRef("http://www.w3.org/2004/02/skos/core#altLabel"))].sort()
        chem["abbrev"] = [abbrev for abbrev in self.app.db.objects(chem["chem"], rdflib.URIRef("http://www.w3.org/2004/02/skos/core#notation"))].sort()
        chem.pop("chem", None)
    self.assertCountEqual(expected_materials, materials)

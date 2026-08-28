# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ontosynthesis_cbu_conversion.py
# region: build_cbu_json_from_graph (lines 287-377, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, Literal
from rdflib.namespace import OWL

for mop in graph.subjects(RDF.type, mop_type_uri):
    print(f"Found MOP: {mop}")
    direct_mops_found += 1
    if _is_guest_mop(mop):
        continue
    ccdc_vals = list(graph.objects(mop, URIRef(str(ONTOMOPS) + "hasCCDCNumber")))
    ccdc = str(ccdc_vals[0]) if ccdc_vals else "N/A"

    if ccdc == "N/A":
        continue

    direct_mops_found += 1
    print(f"Found MOP {mop} with CCDC {ccdc}")

    aliases = _collect_input_aliases_for_mop(mop)

    # Get all CBUs for this MOP
    cbu_formulas = []
    cbu_names = []

    for cbu in graph.objects(mop, URIRef(str(ONTOMOPS) + "hasChemicalBuildingUnit")):
        # Get the formula
        formula_vals = list(graph.objects(cbu, URIRef(str(ONTOMOPS) + "hasCBUFormula")))
        formula = str(formula_vals[0]) if formula_vals else "N/A"

        print(f"Debug: CBU {cbu}, formula_vals: {formula_vals}, formula: {formula}")

        # Get names from labels
        names = []
        for label in graph.objects(cbu, RDFS.label):
            names.append(str(label))

        # Get alternative names - each should be a separate literal
        for alt_name_literal in graph.objects(cbu, URIRef(str(ONTOSYN) + "hasAlternativeNames")):
            alt_name_str = str(alt_name_literal).strip()
            # Remove surrounding quotes if present
            if alt_name_str.startswith('"') and alt_name_str.endswith('"'):
                alt_name_str = alt_name_str[1:-1]
            if alt_name_str and alt_name_str not in names:
                names.append(alt_name_str)

        # Get chemical formula if available
        for chem_formula in graph.objects(cbu, URIRef(str(ONTOSYN) + "hasChemicalFormula")):
            chem_formula_str = str(chem_formula).strip()
            if chem_formula_str and chem_formula_str not in names:
                names.append(chem_formula_str)

        # Also check owl:sameAs links to chemical inputs for additional information
        for chem_input in graph.objects(cbu, OWL.sameAs):
            # Additional labels from chemical inputs
            for ci_label in graph.objects(chem_input, RDFS.label):
                ci_label_str = str(ci_label).strip()
                if ci_label_str and ci_label_str not in names:
                    names.append(ci_label_str)

            # Alternative names from chemical inputs
            for ci_alt_literal in graph.objects(chem_input, URIRef(str(ONTOSYN) + "hasAlternativeNames")):
                alt_name_str = str(ci_alt_literal).strip()
                # Remove surrounding quotes if present
                if alt_name_str.startswith('"') and alt_name_str.endswith('"'):
                    alt_name_str = alt_name_str[1:-1]
                if alt_name_str and alt_name_str not in names:
                    names.append(alt_name_str)

            # Chemical formula from chemical inputs
            for ci_formula in graph.objects(chem_input, URIRef(str(ONTOSYN) + "hasChemicalFormula")):
                ci_formula_str = str(ci_formula).strip()
                if ci_formula_str and ci_formula_str not in names:
                    names.append(ci_formula_str)

        cbu_formulas.append(formula)
        cbu_names.append(names)

    # Sort CBUs by formula for consistency
    cbu_data = list(zip(cbu_formulas, cbu_names))
    cbu_data.sort(key=lambda x: x[0])

    if len(cbu_data) >= 1:
        cbu_data[0] = (cbu_data[0][0], _augment_cbu_names(cbu_data[0][0], cbu_data[0][1], aliases))
    if len(cbu_data) >= 2:
        cbu_data[1] = (cbu_data[1][0], _augment_cbu_names(cbu_data[1][0], cbu_data[1][1], aliases))

    entry = {
        "mopCCDCNumber": ccdc,
        "cbuFormula1": cbu_data[0][0] if len(cbu_data) > 0 else "N/A",
        "cbuSpeciesNames1": cbu_data[0][1] if len(cbu_data) > 0 else [],
        "cbuFormula2": cbu_data[1][0] if len(cbu_data) > 1 else "N/A",
        "cbuSpeciesNames2": cbu_data[1][1] if len(cbu_data) > 1 else [],
    }

    procedures.append(entry)

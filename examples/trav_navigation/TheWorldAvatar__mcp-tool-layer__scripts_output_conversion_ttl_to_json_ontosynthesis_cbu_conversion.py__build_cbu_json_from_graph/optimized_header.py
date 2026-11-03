# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ontosynthesis_cbu_conversion.py
# region: build_cbu_json_from_graph (lines 287-377, stratum trav_navigation)
# licence of the source repository: see meta.json
#
# graph/ONTOMOPS/ONTOSYN/mop_type_uri/procedures/direct_mops_found are
# restored from the enclosing function build_cbu_json_from_graph (the
# region extractor could not carry them: ONTOMOPS/mop_type_uri live above
# the region's own line range, lines 46/280 of the real file; `procedures`/
# `direct_mops_found` are initialised at lines 276/286, just above; `graph`
# is the enclosing function's own parameter, so the region is itself a
# nested closure over it). The three helper closures the region calls
# (_is_guest_mop, _collect_input_aliases_for_mop, _augment_cbu_names) keep
# their real logic verbatim in mop_helpers.py (see that file's header).
from rdflib import Namespace, URIRef, RDF, RDFS, OWL

from mop_helpers import make_helpers

ONTOMOPS = Namespace("https://www.theworldavatar.com/kg/ontomops/")
ONTOSYN = Namespace("https://www.theworldavatar.com/kg/OntoSyn/")
mop_type_uri = URIRef(str(ONTOMOPS) + "MetalOrganicPolyhedron")


def run(graph):
    _is_guest_mop, _collect_input_aliases_for_mop, _augment_cbu_names = make_helpers(graph)
    procedures = []
    direct_mops_found = 0

    for mop in graph.subjects(RDF.type, mop_type_uri):
        print(f"Found MOP: {mop}")
        direct_mops_found += 1
        if _is_guest_mop(mop):
            continue
        ccdc = str(graph.value(mop, ONTOMOPS.hasCCDCNumber, default="N/A"))

        if ccdc == "N/A":
            continue

        direct_mops_found += 1
        print(f"Found MOP {mop} with CCDC {ccdc}")

        aliases = _collect_input_aliases_for_mop(mop)

        # Get all CBUs for this MOP
        cbu_data = []

        for cbu in graph.objects(mop, ONTOMOPS.hasChemicalBuildingUnit):
            # Get the formula
            formula_vals = list(graph.objects(cbu, ONTOMOPS.hasCBUFormula))
            formula = str(formula_vals[0]) if formula_vals else "N/A"

            print(f"Debug: CBU {cbu}, formula_vals: {formula_vals}, formula: {formula}")

            # Get names from labels
            names = [str(label) for label in graph.objects(cbu, RDFS.label)]

            def add_names(values, unquote=False):
                for value in values:
                    name = str(value).strip()
                    # Remove surrounding quotes if present
                    if unquote and name.startswith('"') and name.endswith('"'):
                        name = name[1:-1]
                    if name and name not in names:
                        names.append(name)

            # Get alternative names - each should be a separate literal
            add_names(graph.objects(cbu, ONTOSYN.hasAlternativeNames), unquote=True)
            # Get chemical formula if available
            add_names(graph.objects(cbu, ONTOSYN.hasChemicalFormula))

            # Also check owl:sameAs links to chemical inputs for additional information
            for chem_input in graph.objects(cbu, OWL.sameAs):
                # Additional labels from chemical inputs
                add_names(graph.objects(chem_input, RDFS.label))
                # Alternative names from chemical inputs
                add_names(graph.objects(chem_input, ONTOSYN.hasAlternativeNames), unquote=True)
                # Chemical formula from chemical inputs
                add_names(graph.objects(chem_input, ONTOSYN.hasChemicalFormula))

            cbu_data.append((formula, names))

        # Sort CBUs by formula for consistency
        cbu_data = sorted(cbu_data, key=lambda x: x[0])[:2]
        (formula1, names1), (formula2, names2) = [
            (formula, _augment_cbu_names(formula, names, aliases)) for formula, names in cbu_data
        ] + [("N/A", []), ("N/A", [])][len(cbu_data):]

        procedures.append({
            "mopCCDCNumber": ccdc,
            "cbuFormula1": formula1,
            "cbuSpeciesNames1": names1,
            "cbuFormula2": formula2,
            "cbuSpeciesNames2": names2,
        })

    return procedures

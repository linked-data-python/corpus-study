# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ontosynthesis_cbu_conversion.py
# region: main (lines 629-728, stratum trav_navigation)
# licence of the source repository: see meta.json
import json
import sys
from rdflib import Graph, Namespace, URIRef, RDF, RDFS, Literal

def main():
    """Main function to build complete CBU JSON."""
    print("=== Building CBU JSON ===")

    # Load TTL files from the actual data structure
    import sys
    if len(sys.argv) > 1:
        hash_value = sys.argv[1]
        ttl_files = [f"data/{hash_value}/cbu_derivation/integrated/*.ttl"]
    else:
        # Default to a known hash for testing
        hash_value = "178ef569"
        ttl_files = [f"data/{hash_value}/cbu_derivation/integrated/*.ttl"]

    # Expand glob patterns
    import glob
    expanded_files = []
    for pattern in ttl_files:
        expanded_files.extend(glob.glob(pattern))

    if not expanded_files:
        print(f"No TTL files found for hash {hash_value}")
        return

    print(f"Loading {len(expanded_files)} TTL files for hash {hash_value}")
    graph = load_ttl_files(expanded_files)

    # For integrated TTL files, use direct processing
    print("Processing integrated TTL files directly...")
    procedures = []

    ONTOMOPS = Namespace("https://www.theworldavatar.com/kg/ontomops/")
    RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

    for mop in graph.subjects(RDF.type, URIRef(str(ONTOMOPS) + "MetalOrganicPolyhedron")):
        ccdc_vals = list(graph.objects(mop, URIRef(str(ONTOMOPS) + "hasCCDCNumber")))
        ccdc = str(ccdc_vals[0]) if ccdc_vals else "N/A"

        if ccdc == "N/A":
            continue

        # Get all CBUs for this MOP
        cbu_data = []
        for cbu in graph.objects(mop, URIRef(str(ONTOMOPS) + "hasChemicalBuildingUnit")):
            # Get the formula
            formula_vals = list(graph.objects(cbu, URIRef(str(ONTOMOPS) + "hasCBUFormula")))
            formula = str(formula_vals[0]) if formula_vals else "N/A"

            # Get names from labels
            names = []
            for label in graph.objects(cbu, RDFS.label):
                names.append(str(label))

            cbu_data.append((formula, names))

        # Sort CBUs by formula for consistency
        cbu_data.sort(key=lambda x: x[0])

        entry = {
            "mopCCDCNumber": ccdc,
            "cbuFormula1": cbu_data[0][0] if len(cbu_data) > 0 else "N/A",
            "cbuSpeciesNames1": cbu_data[0][1] if len(cbu_data) > 0 else [],
            "cbuFormula2": cbu_data[1][0] if len(cbu_data) > 1 else "N/A",
            "cbuSpeciesNames2": cbu_data[1][1] if len(cbu_data) > 1 else [],
        }

        procedures.append(entry)

    json_data = {"synthesisProcedures": procedures}

    # Fix cases where chemical names were incorrectly placed in formula fields
    for procedure in json_data["synthesisProcedures"]:
        # Check cbuFormula1
        if procedure.get("cbuFormula1") and procedure["cbuFormula1"] != "N/A":
            formula = procedure["cbuFormula1"]
            # If formula doesn't start with [ (indicating a chemical formula), it's likely a chemical name
            if not formula.startswith("["):
                # Move the chemical name to species names list
                if formula not in procedure.get("cbuSpeciesNames1", []):
                    procedure["cbuSpeciesNames1"].append(formula)
                # Clear the formula field
                procedure["cbuFormula1"] = "N/A"

        # Check cbuFormula2
        if procedure.get("cbuFormula2") and procedure["cbuFormula2"] != "N/A":
            formula = procedure["cbuFormula2"]
            # If formula doesn't start with [ (indicating a chemical formula), it's likely a chemical name
            if not formula.startswith("["):
                # Move the chemical name to species names list
                if formula not in procedure.get("cbuSpeciesNames2", []):
                    procedure["cbuSpeciesNames2"].append(formula)
                # Clear the formula field
                procedure["cbuFormula2"] = "N/A"

    # Save to file
    with open("converted_cbu.json", "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"\nComplete CBU JSON built with {len(json_data['synthesisProcedures'])} synthesis procedures")
    print("Output saved to converted_cbu.json")

# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/agents/mops/cbu_derivation/integration.py
# region: _write_integrated_ttl (lines 663-685, stratum add_isolated)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, Literal
from rdflib.namespace import RDF, RDFS

for iri_str, lbl, is_generated in selected_cbus:
    try:
        cbu_ref = __import__('rdflib').term.URIRef(iri_str)
    except Exception:
        continue

    outg.add((mop_subject, ONTOMOPS.hasChemicalBuildingUnit, cbu_ref))
    outg.add((cbu_ref, RDF.type, ONTOMOPS.ChemicalBuildingUnit))

    # Always add label if present (including empty string), but only add formula if non-empty
    if lbl is not None:
        outg.add((cbu_ref, RDFS.label, Literal(lbl)))
    if lbl:
        try:
            outg.add((cbu_ref, ONTOMOPS.hasCBUFormula, Literal(lbl)))
        except Exception:
            pass

    # For generated CBUs, also add as ChemicalInput type
    if is_generated:
        ONTOSYN = Namespace("https://www.theworldavatar.com/kg/OntoSyn/")
        outg.add((cbu_ref, RDF.type, ONTOSYN.ChemicalInput))
        print(f"[INTEGRATION] Created new CBU with IRI: {iri_str}")

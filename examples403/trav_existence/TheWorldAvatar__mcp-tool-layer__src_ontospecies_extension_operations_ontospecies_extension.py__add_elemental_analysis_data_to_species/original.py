# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : src/ontospecies_extension/operations/ontospecies_extension.py
# region: add_elemental_analysis_data_to_species (lines 356-411, stratum trav_existence)
# licence of the source repository: see meta.json
from typing import Optional, List, Tuple
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
OS  = Namespace("http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#")

def add_elemental_analysis_data_to_species(
    species_iri: str,
    data_label: str,
    calculated_value_text: Optional[str] = None,
    experimental_value_text: Optional[str] = None,
    empirical_molecular_formula: Optional[str] = None,
) -> str:
    with locked_graph() as g:
        # Basic validations
        if not species_iri or not data_label:
            return "ERROR: species_iri and data_label are required."
        if not _is_abs_iri(species_iri):
            return "ERROR: species_iri must be an absolute IRI."

        species_ref = URIRef(species_iri)

        # Check if species exists
        exists = any(g.triples((species_ref, RDF.type, _class(OS, "Species"))))
        if not exists:
            catalog = _list_species_summaries(g, 20)
            return (
                f"ERROR: target species not found.\n"
                f"Requested: {species_iri}\n"
                f"Create the species first, then retry.\n"
                f"Existing Species (up to 20):\n{catalog}"
            )

        # Create EA node
        ea = _mint_hash_iri("ElementalAnalysisData")
        _ensure_type_with_label(g, ea, _class(OS, "ElementalAnalysisData"), data_label)

        # Calculated WeightPercentage node
        if calculated_value_text:
            wp_c = _mint_hash_iri("WeightPercentage")
            _ensure_type_with_label(g, wp_c, _class(OS, "WeightPercentage"), "Calculated")
            g.set((wp_c, _class(OS, "hasWeightPercentageCalculatedValue"), Literal(calculated_value_text)))
            g.add((ea, _class(OS, "hasWeightPercentageCalculated"), wp_c))

        # Experimental WeightPercentage node
        if experimental_value_text:
            wp_e = _mint_hash_iri("WeightPercentage")
            _ensure_type_with_label(g, wp_e, _class(OS, "WeightPercentage"), "Experimental")
            g.set((wp_e, _class(OS, "hasWeightPercentageExperimentalValue"), Literal(experimental_value_text)))
            g.add((ea, _class(OS, "hasWeightPercentageExperimental"), wp_e))

        # Empirical molecular formula node (optional)
        if empirical_molecular_formula:
            mf = _mint_hash_iri("MolecularFormula")
            _ensure_type_with_label(g, mf, _class(OS, "MolecularFormula"), empirical_molecular_formula)
            g.set((mf, _class(OS, "hasMolecularFormulaValue"), Literal(empirical_molecular_formula)))
            g.add((species_ref, _class(OS, "hasMolecularFormula"), mf))

        # Attach EA to species
        g.add((species_ref, _class(OS, "hasElementalAnalysisData"), ea))

        return str(ea)

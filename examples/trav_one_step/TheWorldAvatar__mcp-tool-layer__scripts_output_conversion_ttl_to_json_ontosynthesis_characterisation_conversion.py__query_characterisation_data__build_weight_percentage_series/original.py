# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ontosynthesis_characterisation_conversion.py
# region: query_characterisation_data._build_weight_percentage_series (lines 234-274, stratum trav_one_step)
# licence of the source repository: see meta.json
import re
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

def _build_weight_percentage_series(species: URIRef) -> tuple[str, str]:
    calc_parts: Dict[str, str] = {}
    exp_parts: Dict[str, str] = {}
    calc_full: List[str] = []
    exp_full: List[str] = []

    for ead in graph.objects(species, ontospecies.hasElementalAnalysisData):
        for wp in graph.objects(ead, ontospecies.hasWeightPercentageCalculated):
            label = next((str(v) for v in graph.objects(wp, RDFS.label)), "")
            for value in graph.objects(wp, ontospecies.hasWeightPercentageCalculatedValue):
                text = str(value).strip()
                if not text:
                    continue
                if re.search(r"[A-Za-z]\s+\d", text):
                    calc_full.append(text)
                else:
                    element = _infer_element_symbol(label)
                    if element:
                        calc_parts[element] = text
        for wp in graph.objects(ead, ontospecies.hasWeightPercentageExperimental):
            label = next((str(v) for v in graph.objects(wp, RDFS.label)), "")
            for value in graph.objects(wp, ontospecies.hasWeightPercentageExperimentalValue):
                text = str(value).strip()
                if not text:
                    continue
                if re.search(r"[A-Za-z]\s+\d", text):
                    exp_full.append(text)
                else:
                    element = _infer_element_symbol(label)
                    if element:
                        exp_parts[element] = text

    def _format(full_values: List[str], parts: Dict[str, str]) -> str:
        if full_values:
            # Prefer the richest combined string already closest to the benchmark format.
            return max(full_values, key=len)
        order = ["C", "H", "N", "O", "S", "P"]
        assembled = [f"{el}, {parts[el]}" for el in order if el in parts]
        return "; ".join(assembled) if assembled else "N/A"

    return _format(calc_full, calc_parts), _format(exp_full, exp_parts)

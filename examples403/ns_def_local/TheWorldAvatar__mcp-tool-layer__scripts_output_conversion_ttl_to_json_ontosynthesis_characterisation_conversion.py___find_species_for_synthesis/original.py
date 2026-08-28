# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ontosynthesis_characterisation_conversion.py
# region: _find_species_for_synthesis (lines 81-140, stratum ns_def_local)
# licence of the source repository: see meta.json
from typing import Dict, List, Any, Optional
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

def _find_species_for_synthesis(graph: Graph, synth: URIRef) -> List[URIRef]:
    q = f"""
    PREFIX ontosyn: <https://www.theworldavatar.com/kg/OntoSyn/>
    PREFIX ontospecies: <http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#>
    SELECT DISTINCT ?uri WHERE {{
      <{synth}> ontosyn:hasChemicalOutput ?uri .
      ?uri a ontospecies:Species .
    }}
    """
    direct_hits = _select_uris(graph, q)
    if direct_hits:
        return direct_hits

    seen: set[str] = set()
    resolved: List[URIRef] = []

    def _add_species(uri: URIRef) -> None:
        key = str(uri)
        if key not in seen:
            seen.add(key)
            resolved.append(uri)

    # Fallback 1: resolve species by synthesis label / ChemicalOutput label matching.
    ontosyn = Namespace("https://www.theworldavatar.com/kg/OntoSyn/")
    ontospecies = Namespace("http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#")

    def _normalize_product_name(value: str) -> str:
        text = str(value or "").strip().lower()
        if text.endswith(" synthesis"):
            text = text[: -len(" synthesis")].strip()
        return text

    target_names: set[str] = set()
    for label in graph.objects(synth, RDFS.label):
        norm = _normalize_product_name(str(label))
        if norm:
            target_names.add(norm)
    for out in graph.objects(synth, ontosyn.hasChemicalOutput):
        for label in graph.objects(out, RDFS.label):
            norm = _normalize_product_name(str(label))
            if norm:
                target_names.add(norm)

    if not target_names:
        return resolved

    for species in graph.subjects(RDF.type, ontospecies.Species):
        species_names: set[str] = set()
        for label in graph.objects(species, RDFS.label):
            norm = _normalize_product_name(str(label))
            if norm:
                species_names.add(norm)
        for product_name in graph.objects(species, ontospecies.hasProductName):
            norm = _normalize_product_name(str(product_name))
            if norm:
                species_names.add(norm)
        if species_names & target_names:
            _add_species(URIRef(str(species)))

    return resolved

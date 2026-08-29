# Context shim (see meta.json): `_is_guest_mop`, `_collect_input_aliases_for_mop`,
# `_augment_cbu_names` and the two small helpers they call
# (`_uniq_keep_order`, `_split_alt_names`), copied verbatim (only reformatted
# for str-concatenation constants) from build_cbu_json_from_graph in
# TheWorldAvatar/mcp-tool-layer@c440a33e08 :
# scripts/output_conversion_ttl_to_json/ontosynthesis_cbu_conversion.py
# (lines 69-186). In the real source these are nested inside
# build_cbu_json_from_graph, closing over its `graph` parameter -- the
# region under test (lines 287-377) calls them the same way, unqualified.
# `make_helpers(graph)` reproduces that closure instead of adding a `graph`
# argument the originals never had. Identical for both representations
# (imported by original.py and translated.ldpy alike); excluded from
# surface metrics -- no logic invented, nothing simplified.
from typing import Any, Dict, List

from rdflib import RDF, RDFS, URIRef

_ONTOSYN = "https://www.theworldavatar.com/kg/OntoSyn/"


def make_helpers(graph):
    def _uniq_keep_order(items: List[str]) -> List[str]:
        out: List[str] = []
        seen = set()
        for item in items:
            text = str(item or "").strip()
            if not text or text in seen:
                continue
            seen.add(text)
            out.append(text)
        return out

    def _split_alt_names(value: str) -> List[str]:
        text = str(value or "").strip()
        if not text:
            return []
        if ";" in text:
            return [part.strip() for part in text.split(";") if part.strip()]
        return [text]

    def _is_guest_mop(mop: URIRef) -> bool:
        labels = [str(v).strip() for v in graph.objects(mop, RDFS.label)]
        label_text = " ".join(labels)
        return "·" in label_text

    def _collect_input_aliases_for_mop(mop: URIRef) -> Dict[str, List[str]]:
        synths = set()
        for chem_out in graph.subjects(URIRef(_ONTOSYN + "isRepresentedBy"), mop):
            for synth in graph.subjects(URIRef(_ONTOSYN + "hasChemicalOutput"), chem_out):
                synths.add(synth)

        if not synths:
            mop_labels = [str(v).strip() for v in graph.objects(mop, RDFS.label) if str(v).strip()]
            normalized_targets = {f"{label.lower()} synthesis" for label in mop_labels}
            for synth in graph.subjects(RDF.type, URIRef(_ONTOSYN + "ChemicalSynthesis")):
                synth_labels = [str(v).strip() for v in graph.objects(synth, RDFS.label) if str(v).strip()]
                if any(lbl.lower() in normalized_targets for lbl in synth_labels):
                    synths.add(synth)

        organic_names: List[str] = []
        metal_names: List[str] = []
        seen_chems = set()

        def _record_chemical(chem: URIRef) -> None:
            chem_key = str(chem)
            if chem_key in seen_chems:
                return
            seen_chems.add(chem_key)

            labels = [str(v).strip() for v in graph.objects(chem, RDFS.label) if str(v).strip()]
            alt_names: List[str] = []
            for alt in graph.objects(chem, URIRef(_ONTOSYN + "hasAlternativeNames")):
                alt_names.extend(_split_alt_names(str(alt)))
            descriptions = [
                str(v).strip().lower()
                for v in graph.objects(chem, URIRef(_ONTOSYN + "hasChemicalDescription"))
                if str(v).strip()
            ]
            merged_text = " ".join(labels + alt_names + descriptions).lower()
            if not merged_text:
                return
            if any(token in merged_text for token in ["solvent", "guest molecule", "guest"]):
                return

            names = _uniq_keep_order(labels + alt_names)
            if not names:
                return

            is_metal = any(token in merged_text for token in ["metal precursor", "voso4", "vanadyl sulfate"])
            is_organic = any(
                token in merged_text
                for token in ["linker", "ligand", "carboxylate", "tetracarboxylic acid"]
            ) or any(name.upper().startswith("H4") for name in names)

            if is_metal:
                metal_names.extend(names)
            elif is_organic:
                organic_names.extend(names)

        for synth in synths:
            for chem in graph.objects(synth, URIRef(_ONTOSYN + "hasChemicalInput")):
                if isinstance(chem, URIRef):
                    _record_chemical(chem)
            for step in graph.objects(synth, URIRef(_ONTOSYN + "hasSynthesisStep")):
                for chem in graph.objects(step, URIRef(_ONTOSYN + "hasAddedChemicalInput")):
                    if isinstance(chem, URIRef):
                        _record_chemical(chem)

        return {
            "organic": _uniq_keep_order(organic_names),
            "metal": _uniq_keep_order(metal_names),
        }

    def _augment_cbu_names(formula: str, names: List[str], aliases: Dict[str, List[str]]) -> List[str]:
        normalized = _uniq_keep_order([str(n).strip() for n in names if str(n).strip()])
        non_formula = [n for n in normalized if n != formula]
        if "v6o6" in formula.lower():
            inferred = aliases.get("metal", [])
        else:
            inferred = aliases.get("organic", [])
        if non_formula:
            return _uniq_keep_order(non_formula + inferred)
        if inferred:
            return _uniq_keep_order(inferred)
        return [n for n in normalized if n != formula]

    return _is_guest_mop, _collect_input_aliases_for_mop, _augment_cbu_names

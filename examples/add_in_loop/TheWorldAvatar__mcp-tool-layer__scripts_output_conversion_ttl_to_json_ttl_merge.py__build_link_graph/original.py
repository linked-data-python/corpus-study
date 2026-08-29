# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ttl_merge.py
# region: build_link_graph (lines 350-423, stratum add_in_loop)
# licence of the source repository: see meta.json
from typing import Dict, Iterable, List, Tuple, Set
import hashlib
from rdflib import BNode, Graph, Namespace, RDF, RDFS, URIRef, Literal
from _context import _bind_prefixes
RDF_NS = RDF
RDFS_NS = RDFS
ONTOSYN = Namespace("https://www.theworldavatar.com/kg/OntoSyn/")
ONTOMOPS = Namespace("https://www.theworldavatar.com/kg/ontomops/")
ONTOSPECIES = Namespace("http://www.theworldavatar.com/ontology/ontospecies/OntoSpecies.owl#")

def build_link_graph(merged_graph: Graph) -> Graph:
    """
    Build a debugging subgraph containing only selected instance types and
    their direct connections. The selected instance types are:
    - ontospecies:Species
    - ontosyn:ChemicalSynthesis
    - ontomops:MetalOrganicPolyhedron
    - ontomops:ChemicalBuildingUnit

    Connections preserved:
    - Any triple where both subject and object are selected instances
    - For convenience, also include the specific bridging pattern:
      ChemicalSynthesis --ontosyn:hasChemicalOutput--> _:x --ontosyn:isRepresentedBy--> MetalOrganicPolyhedron
      (without asserting the type of the blank node)
    - Include rdf:type and rdfs:label of selected instance nodes for readability
    """
    g = merged_graph
    lg = Graph()
    _bind_prefixes(lg)

    allowed_types: Tuple[URIRef, ...] = (
        ONTOSPECIES.Species,
        ONTOSYN.ChemicalSynthesis,
        ONTOMOPS.MetalOrganicPolyhedron,
        ONTOMOPS.ChemicalBuildingUnit,
    )

    # Identify selected instance nodes
    selected: Set = set()
    for t in allowed_types:
        for s in g.subjects(RDF_NS.type, t):
            selected.add(s)

    # Add type and label for selected nodes
    for s in selected:
        for t in g.objects(s, RDF_NS.type):
            if t in allowed_types:
                lg.add((s, RDF_NS.type, t))
        for lab in g.objects(s, RDFS_NS.label):
            lg.add((s, RDFS_NS.label, lab))

    # Add direct connections among selected nodes
    for (s, p, o) in g.triples((None, None, None)):
        if s in selected and o in selected:
            lg.add((s, p, o))

    # Add bridging synthesis->ChemicalOutput->MOP connections
    for synth in [n for n in selected if (n, RDF_NS.type, ONTOSYN.ChemicalSynthesis) in g]:
        # Include hasChemicalInput connections for debugging visibility
        for chem_input in g.objects(synth, ONTOSYN.hasChemicalInput):
            lg.add((synth, ONTOSYN.hasChemicalInput, chem_input))
            # include minimal info for ChemicalInput nodes
            if (chem_input, RDF_NS.type, ONTOSYN.ChemicalInput) in g:
                lg.add((chem_input, RDF_NS.type, ONTOSYN.ChemicalInput))
            for lab in g.objects(chem_input, RDFS_NS.label):
                lg.add((chem_input, RDFS_NS.label, lab))

        for chem_out in g.objects(synth, ONTOSYN.hasChemicalOutput):
            # Only bridge to MOP if the object is a selected MOP
            for mop in g.objects(chem_out, ONTOSYN.isRepresentedBy):
                if mop in selected and (mop, RDF_NS.type, ONTOMOPS.MetalOrganicPolyhedron) in g:
                    # Skolemize blank ChemicalOutput nodes for readability in debug graph
                    skolem_out = chem_out
                    if isinstance(chem_out, BNode):
                        synth_id = str(synth)
                        mop_id = str(mop)
                        h = hashlib.sha1((synth_id + "|" + mop_id).encode("utf-8")).hexdigest()
                        skolem_out = URIRef(
                            f"https://www.theworldavatar.com/kg/OntoSyn/instance/ChemicalOutput/{h}"
                        )
                    lg.add((synth, ONTOSYN.hasChemicalOutput, skolem_out))
                    lg.add((skolem_out, ONTOSYN.isRepresentedBy, mop))

    return lg

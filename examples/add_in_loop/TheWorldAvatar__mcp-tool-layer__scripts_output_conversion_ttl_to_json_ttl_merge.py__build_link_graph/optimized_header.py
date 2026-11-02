# Extracted from TheWorldAvatar/mcp-tool-layer@c440a33e08 : scripts/output_conversion_ttl_to_json/ttl_merge.py
# region: build_link_graph (lines 350-423, stratum add_in_loop)
# licence of the source repository: see meta.json
from typing import Tuple, Set
import hashlib
from rdflib import BNode, Graph, Namespace, RDF, RDFS, URIRef
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
    selected: Set = {s for t in allowed_types for s in g.subjects(RDF_NS.type, t)}

    # Add type and label for selected nodes
    for t in allowed_types:
        lg += g.triples((None, RDF_NS.type, t))
    for s in selected:
        lg += g.triples((s, RDFS_NS.label, None))

    # Add direct connections among selected nodes
    lg += [(s, p, o) for (s, p, o) in g if s in selected and o in selected]

    # Add bridging synthesis->ChemicalOutput->MOP connections
    for synth in g.subjects(RDF_NS.type, ONTOSYN.ChemicalSynthesis):
        # Include hasChemicalInput connections for debugging visibility
        for chem_input in g.objects(synth, ONTOSYN.hasChemicalInput):
            lg.add((synth, ONTOSYN.hasChemicalInput, chem_input))
            # include minimal info for ChemicalInput nodes
            lg += g.triples((chem_input, RDF_NS.type, ONTOSYN.ChemicalInput))
            lg += g.triples((chem_input, RDFS_NS.label, None))

        for chem_out in g.objects(synth, ONTOSYN.hasChemicalOutput):
            # Only bridge to MOP if the object is a selected MOP
            for mop in g.objects(chem_out, ONTOSYN.isRepresentedBy):
                if (mop, RDF_NS.type, ONTOMOPS.MetalOrganicPolyhedron) in g:
                    # Skolemize blank ChemicalOutput nodes for readability in debug graph
                    skolem_out = chem_out
                    if isinstance(chem_out, BNode):
                        h = hashlib.sha1(f"{synth}|{mop}".encode("utf-8")).hexdigest()
                        skolem_out = ONTOSYN[f"instance/ChemicalOutput/{h}"]
                    lg += [(synth, ONTOSYN.hasChemicalOutput, skolem_out),
                           (skolem_out, ONTOSYN.isRepresentedBy, mop)]

    return lg

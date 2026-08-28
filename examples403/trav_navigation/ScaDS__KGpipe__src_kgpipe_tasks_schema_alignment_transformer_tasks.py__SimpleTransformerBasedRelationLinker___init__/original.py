# Extracted from ScaDS/KGpipe@67ca171cfd : src/kgpipe_tasks/schema_alignment/transformer_tasks.py
# region: SimpleTransformerBasedRelationLinker.__init__ (lines 16-39, stratum trav_navigation)
# licence of the source repository: see meta.json
from sentence_transformers import SentenceTransformer, util
from rdflib import Graph, OWL, RDFS, RDF

def __init__(self, ontology_file, model_name="all-MiniLM-L6-v2"):
    self.model = SentenceTransformer(model_name)

    g = Graph()
    g.parse(ontology_file)

    ontology_relations = {}
    # Extract ObjectProperties
    for s in g.subjects(RDF.type, OWL.ObjectProperty):
        label = g.value(s, RDFS.label)
        if label:
            ontology_relations[str(label)] = str(s)

    # Extract DatatypeProperties
    for s in g.subjects(RDF.type, OWL.DatatypeProperty):
        label = g.value(s, RDFS.label)
        if label:
            ontology_relations[str(label)] = str(s)

    self.ontology_relations = ontology_relations

    # Compute embeddings for ontology predicates
    self.ontology_labels = list(ontology_relations.keys())
    self.ontology_embeddings = self.model.encode(self.ontology_labels, convert_to_tensor=True)

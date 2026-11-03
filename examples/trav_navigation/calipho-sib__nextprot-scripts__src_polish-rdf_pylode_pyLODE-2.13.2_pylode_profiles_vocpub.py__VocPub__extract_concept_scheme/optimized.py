# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/vocpub.py
# region: VocPub._extract_concept_scheme (lines 368-460, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DC, DCTERMS, DOAP, OWL, PROV, RDF, RDFS, SDO, SKOS
import markdown

def _extract_concept_scheme(self):
    """Extracts standard SKOS ConceptScheme metadata

    Will interpret an owl:Ontology as a skos:ConceptScheme if run against an OWL document
    """

    self.METADATA.update(creators=set(), contributors=set(), publishers=set())
    text_keys = {
        SKOS.prefLabel: "title", OWL.versionInfo: "versionInfo",
        # dates
        DCTERMS.created: "created", DCTERMS.modified: "modified", DCTERMS.issued: "issued",
        URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix"): "preferredNamespacePrefix",
        URIRef("http://purl.org/vocab/vann/preferredNamespaceUri"): "preferredNamespaceUri",
    }
    for s in self.G.subjects(predicate=RDF.type, object=SKOS.ConceptScheme):
        self.METADATA["uri"] = str(s)
        for p, o in self.G.predicate_objects(subject=s):
            if p in text_keys:
                self.METADATA[text_keys[p]] = str(o)

            if p in (SKOS.definition, SKOS.historyNote):
                key = "description" if p == SKOS.definition else "historyNote"
                self.METADATA[key] = (
                    str(o) if self.outputformat == "md" else markdown.markdown(str(o)))

            if p in (DCTERMS.source, DCTERMS.license):
                self.METADATA[p.split("/")[-1]] = (
                    self._make_formatted_uri(o)  # '<a href="{0}">{0}</a>'.format(str(o))
                    if str(o).startswith("http") else str(o))

            if p == OWL.versionIRI:
                self.METADATA["versionIRI"] = self._make_formatted_uri(o)

            if p == DCTERMS.rights:
                self.METADATA["rights"] = (
                    str(o).replace("Copyright", "&copy;").replace("copyright", "&copy;")
                    .replace("(c)", "&copy;"))

            # Agents
            if p in [DCTERMS.creator, DCTERMS.contributor, DCTERMS.publisher]:
                self.METADATA[p.split("/")[-1] + "s"].add(
                    str(o) if type(o) == Literal else self._make_agent(o))  # Blank Node or URI

            # TODO: cater for other Agent representations

            if p == PROV.wasGeneratedBy:
                for o2 in self.G.objects(subject=o, predicate=DOAP.repository):
                    self.METADATA["repository"] = self._make_formatted_uri(o2)

            if p == SDO.codeRepository:
                self.METADATA["repository"] = self._make_formatted_uri(o)

    if self.METADATA.get("title") is None:
        raise ValueError(
            "Your taxonomy's ConceptScheme does not indicate any form of title. "
            "You must declare one of the following for it: rdfs:label, dct:title, skos:prefLabel"
        )

    if self.COLLECTIONS:
        self.METADATA["has_collections"] = True

    if self.CONCEPTS:
        self.METADATA["has_concepts"] = True

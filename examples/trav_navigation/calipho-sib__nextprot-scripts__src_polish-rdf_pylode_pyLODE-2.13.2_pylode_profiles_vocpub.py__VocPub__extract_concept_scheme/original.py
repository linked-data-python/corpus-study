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

    self.METADATA["creators"] = set()
    self.METADATA["contributors"] = set()
    self.METADATA["publishers"] = set()
    for s in self.G.subjects(predicate=RDF.type, object=SKOS.ConceptScheme):
        self.METADATA["uri"] = str(s)
        for p, o in self.G.predicate_objects(subject=s):
            if p == SKOS.prefLabel:
                self.METADATA["title"] = str(o)

            if p == SKOS.definition:
                if self.outputformat == "md":
                    self.METADATA["description"] = str(o)
                else:
                    self.METADATA["description"] = markdown.markdown(str(o))

            if p == SKOS.historyNote:
                if self.outputformat == "md":
                    self.METADATA["historyNote"] = str(o)
                else:
                    self.METADATA["historyNote"] = markdown.markdown(str(o))

            # dates
            if p in [DCTERMS.created, DCTERMS.modified, DCTERMS.issued]:
                date_type = p.split("/")[-1]
                self.METADATA[date_type] = str(o)

            if p == DCTERMS.source:
                if str(o).startswith('http'):
                    self.METADATA["source"] = self._make_formatted_uri(o)  # '<a href="{0}">{0}</a>'.format(str(o))
                else:
                    self.METADATA["source"] = str(o)

            if p == OWL.versionIRI:
                self.METADATA["versionIRI"] = self._make_formatted_uri(o)

            if p == OWL.versionInfo:
                self.METADATA["versionInfo"] = str(o)

            if p == URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix"):
                self.METADATA["preferredNamespacePrefix"] = str(o)

            if p == URIRef("http://purl.org/vocab/vann/preferredNamespaceUri"):
                self.METADATA["preferredNamespaceUri"] = str(o)

            if p == DCTERMS.license:
                self.METADATA["license"] = (
                    self._make_formatted_uri(o)
                    if str(o).startswith("http")
                    else str(o)
                )

            if p == DCTERMS.rights:
                self.METADATA["rights"] = (
                    str(o)
                        .replace("Copyright", "&copy;")
                        .replace("copyright", "&copy;")
                        .replace("(c)", "&copy;")
                )

            # Agents
            if p in [DCTERMS.creator, DCTERMS.contributor, DCTERMS.publisher]:
                agent_type = p.split("/")[-1] + "s"
                if type(o) == Literal:
                    self.METADATA[agent_type].add(str(o))
                else:  # Blank Node or URI
                    self.METADATA[agent_type].add(self._make_agent(o))

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

    if len(self.COLLECTIONS.keys()) > 0:
        self.METADATA["has_collections"] = True

    if len(self.CONCEPTS.keys()) > 0:
        self.METADATA["has_concepts"] = True

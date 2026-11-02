# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/ontdoc.py
# region: OntDoc._extract_metadata (lines 345-428, stratum trav_navigation)
# licence of the source repository: see meta.json
import markdown
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import DC, DCTERMS, DOAP, OWL, PROF, PROV, RDF, RDFS, SDO, SKOS

# Wrapped in a function (context restoration, meta.json: the region is the
# body of a method, `self` is a free variable of it). The body itself, from the
# `for` line to the end of the file, is what was extracted; only that `for`
# line is indented by one space, so that it can sit under the `def`.
def extract_metadata_region(self):
 for s in self.G.subjects(predicate=RDF.type, object=OWL.Ontology):
    s_str = str(s)  # this is the Ontology's URI
    self.METADATA["uri"] = s_str

    for p, o in self.G.predicate_objects(subject=s):
        if p == OWL.imports:
            self.METADATA["imports"].add(self._make_formatted_uri(o))

        if p == DCTERMS.title:
            self.METADATA["title"] = str(o)

        if p == DCTERMS.description:
            if self.outputformat == "md":
                self.METADATA["description"] = str(o)
            elif self.outputformat == "adoc":
                self.METADATA["description"] = str(o)
            else:
                self.METADATA["description"] = markdown.markdown(str(o))

        if p == SKOS.historyNote:
            if self.outputformat == "md":
                self.METADATA["historyNote"] = str(o)
            elif self.outputformat == "adoc":
                self.METADATA["historyNote"] = str(o)
            else:
                self.METADATA["historyNote"] = markdown.markdown(str(o))

        # dates
        if p in [DCTERMS.created, DCTERMS.modified, DCTERMS.issued]:
            date_type = p.split("/")[-1]
            self.METADATA[date_type] = str(o)

        if p == DCTERMS.source:
            if str(o).startswith('http'):
                self.METADATA["source"] = self._make_formatted_uri(o)
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
        if p in [
            DCTERMS.creator, DCTERMS.contributor, DCTERMS.publisher, SDO.editor, SDO.funder, SDO.translator
        ]:
            agent_type = p.split("/")[-1] + "s"
            if type(o) == Literal:
                self.METADATA[agent_type].add(str(o))
            else:  # Blank Node or URI
                self.METADATA[agent_type].add(self._make_agent(o))

        if p == PROV.wasGeneratedBy:
            for o2 in self.G.objects(subject=o, predicate=DOAP.repository):
                self.METADATA["repository"] = self._make_formatted_uri(o2)

        if p == SDO.codeRepository:
            self.METADATA["repository"] = self._make_formatted_uri(o)

    if self.METADATA.get("title") is None:
        self.METADATA["title"] = "{no title found}"

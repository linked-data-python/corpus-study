# Extracted from calipho-sib/nextprot-scripts@f03504ce5e : src/polish-rdf/pylode/pyLODE-2.13.2/pylode/profiles/ontdoc.py
# region: OntDoc._extract_metadata (lines 345-428, stratum trav_navigation)
# licence of the source repository: see meta.json
import markdown
from rdflib import Literal, URIRef
from rdflib.namespace import DCTERMS, DOAP, OWL, PROV, RDF, SDO, SKOS

# Wrapped in a function (context restoration, meta.json: the region is the
# body of a method, `self` is a free variable of it). The body itself, from the
# `for` line to the end of the file, is what was extracted; only that `for`
# line is indented by one space, so that it can sit under the `def`.
def extract_metadata_region(self):
 text_keys = {
     DCTERMS.title: "title", OWL.versionInfo: "versionInfo",
     # dates
     DCTERMS.created: "created", DCTERMS.modified: "modified", DCTERMS.issued: "issued",
     URIRef("http://purl.org/vocab/vann/preferredNamespacePrefix"): "preferredNamespacePrefix",
     URIRef("http://purl.org/vocab/vann/preferredNamespaceUri"): "preferredNamespaceUri",
 }
 for s in self.G.subjects(predicate=RDF.type, object=OWL.Ontology):
    self.METADATA["uri"] = str(s)  # this is the Ontology's URI

    for p, o in self.G.predicate_objects(subject=s):
        if p == OWL.imports:
            self.METADATA["imports"].add(self._make_formatted_uri(o))

        if p in text_keys:
            self.METADATA[text_keys[p]] = str(o)

        if p in (DCTERMS.description, SKOS.historyNote):
            key = "description" if p == DCTERMS.description else "historyNote"
            self.METADATA[key] = (
                str(o) if self.outputformat in ("md", "adoc") else markdown.markdown(str(o)))

        if p in (DCTERMS.source, DCTERMS.license):
            self.METADATA[p.split("/")[-1]] = (
                self._make_formatted_uri(o) if str(o).startswith("http") else str(o))

        if p == OWL.versionIRI:
            self.METADATA["versionIRI"] = self._make_formatted_uri(o)

        if p == DCTERMS.rights:
            self.METADATA["rights"] = (
                str(o).replace("Copyright", "&copy;").replace("copyright", "&copy;")
                .replace("(c)", "&copy;"))

        # Agents
        if p in [
            DCTERMS.creator, DCTERMS.contributor, DCTERMS.publisher, SDO.editor, SDO.funder, SDO.translator
        ]:
            self.METADATA[p.split("/")[-1] + "s"].add(
                str(o) if type(o) == Literal else self._make_agent(o))  # Blank Node or URI

        if p == PROV.wasGeneratedBy:
            for o2 in self.G.objects(subject=o, predicate=DOAP.repository):
                self.METADATA["repository"] = self._make_formatted_uri(o2)

        if p == SDO.codeRepository:
            self.METADATA["repository"] = self._make_formatted_uri(o)

    if self.METADATA.get("title") is None:
        self.METADATA["title"] = "{no title found}"

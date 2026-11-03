# Extracted from acdh-oeaw/acdh-django-vocabs@60355474bb : vocabs/skos_import.py
# region: SkosImporter.parse_triples (lines 68-116, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import DC, RDFS, SKOS
import context_shim  # noqa: F401 -- restores Graph.preferredLabel, see meta.json
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCT = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")


# Test harness only (see meta.json): the sampled region (kind=statement) is
# the MIDDLE of SkosImporter.parse_triples -- concept_scheme, the two nested
# helpers and `self` are all bound just above it in the real method
# (vocabs/skos_import.py lines 47, 50-64) but fall outside the sampled line
# range (68-116). Reproduced verbatim here (not invented) so the extracted
# statement below has something to run against. `self` is an explicit
# parameter rather than relying on Python's implicit method binding, so the
# driver can hand it any object with a `.language` attribute (see
# driver.py) instead of a full SkosImporter instance. `return concept_scheme`
# is likewise added only so the driver has something to compare -- the real
# method keeps going past line 116 (a "Parsing Collection" section, out of
# this region's range) before it returns anything itself.
def parse_triples(self, g):
    concept_scheme = {}

    def allow_properties(_property):
        """Allow DC and DCT properties"""
        properties = [URIRef('http://purl.org/dc/terms/{}'.format(_property)),
                      URIRef('http://purl.org/dc/elements/1.1/{}'.format(_property))]
        return properties

    def language_check(property_lang):
        """Check for language attributes, if they are absent set language to a specified language"""
        if property_lang:
            if str(property_lang) == "None":
                return self.language
            else:
                return str(property_lang)
        else:
            return self.language

    # --- extracted region begins (parse_triples, lines 68-116) ---
    if (None, RDF.type, SKOS.ConceptScheme) not in g:
        raise Exception("rdf:type skos:ConceptScheme is not found")
    for cs in g.subjects(RDF.type, SKOS.ConceptScheme):
        concept_scheme["identifier"] = str(cs)
        # Set labels properties to recognize all possible labels
        concept_scheme["title"] = [
            {"title": str(title), "lang": language_check(title.language)}
            for _, title in g.preferredLabel(
                cs, labelProperties=(DC.title, RDFS.label, DCT.title, SKOS.prefLabel))]
        for field in ("creator", "contributor", "language", "subject", "publisher"):
            concept_scheme[field] = ";".join(
                value for prop in allow_properties(field) for value in g.objects(cs, prop))
        for license in g.objects(cs, DCT.license):
            concept_scheme["license"] = str(license)
        for field in ("description", "source"):
            concept_scheme[field] = [
                {"name": str(value), "lang": language_check(value.language)}
                for prop in allow_properties(field) for value in g.objects(cs, prop)]
    # --- extracted region ends ---

    return concept_scheme

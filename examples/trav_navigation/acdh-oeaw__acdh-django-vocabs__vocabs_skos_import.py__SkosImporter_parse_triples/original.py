# Extracted from acdh-oeaw/acdh-django-vocabs@60355474bb : vocabs/skos_import.py
# region: SkosImporter.parse_triples (lines 68-116, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF, URIRef
from rdflib.namespace import DC, RDFS, SKOS
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DC = Namespace("http://purl.org/dc/elements/1.1/")
DCT = Namespace("http://purl.org/dc/terms/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")

if (None, RDF.type, SKOS.ConceptScheme) in g:
    for cs in g.subjects(RDF.type, SKOS.ConceptScheme):
        concept_scheme["identifier"] = str(cs)
        titles = []
        # Set labels properties to recognize all possible labels
        for title in g.preferredLabel(
                cs, labelProperties=((DC.title), (RDFS.label), (DCT.title), (SKOS.prefLabel))
        ):
            temp_title = {"title": str(title[1])}
            # If language attribute is absent populate it with a specified language
            if str(title[1].language) == "None":
                temp_title["lang"] = self.language
            else:
                temp_title["lang"] = str(title[1].language)
            titles.append(temp_title)
        concept_scheme["title"] = titles
        concept_scheme["creator"] = ";".join(
            [c for cp in allow_properties('creator') for c in g.objects(cs, cp)])
        concept_scheme["contributor"] = ";".join(
            [contr for contrp in allow_properties('contributor') for contr in g.objects(cs, contrp)])
        concept_scheme["language"] = ";".join(
            [l for lp in allow_properties('language') for l in g.objects(cs, lp)])
        concept_scheme["subject"] = ";".join(
            [s for sp in allow_properties('subject') for s in g.objects(cs, sp)])
        concept_scheme["publisher"] = ";".join(
            [p for pp in allow_properties('publisher') for p in g.objects(cs, pp)])
        for license in g.objects(cs, DCT.license):
            concept_scheme["license"] = str(license)
        descriptions = []
        for descp in allow_properties('description'):
            for d in g.objects(cs, descp):
                temp_desc = {
                    "name": str(d),
                    "lang": language_check(d.language)
                }
                descriptions.append(temp_desc)
        concept_scheme["description"] = descriptions
        sources = []
        for sp in allow_properties('source'):
            for s in g.objects(cs, sp):
                temp_s = {
                    "name": str(s),
                    "lang": language_check(s.language)
                }
                sources.append(temp_s)
        concept_scheme["source"] = sources

else:
    raise Exception("rdf:type skos:ConceptScheme is not found")

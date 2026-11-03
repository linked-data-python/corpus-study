# Extracted from vemonet/rdflib-endpoint@1427c77829 : src/rdflib_endpoint/sparql_router.py
# region: SparqlRouter.prepare_sd_graph (lines 454-455, stratum trav_existence)
# licence of the source repository: see meta.json
from shim import SD, FORMATS, self, sd_subj

triple = (sd_subj, SD.resultFormat, FORMATS.RDF_XML)
if triple not in self.service_description:
    self.service_description.add(triple)

service_description = self.service_description  # exposed for the pilot: see meta.json

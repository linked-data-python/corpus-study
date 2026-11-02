# Extracted from johnjung/metadata_converters@36a81d6a97 : metadata_converters/mepa_edm.py
# region: MepaToEDM._build_cho (lines 201-201, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, DC, DCTERMS, XSD

self.graph.add((self.work_cho, DCTERMS.hasPart, self.recto_cho))

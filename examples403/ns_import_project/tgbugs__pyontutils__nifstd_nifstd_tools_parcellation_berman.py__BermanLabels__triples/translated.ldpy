# Extracted from tgbugs/pyontutils@cb3efcd10f : nifstd/nifstd_tools/parcellation/berman.py
# region: BermanLabels._triples (lines 258-281, stratum ns_import_project)
# licence of the source repository: see meta.json
import rdflib
from nifstd_tools.parcellation import parcCore, Atlas, LabelRoot, Label
from pyontutils.namespaces import NIFRID, ilx, ilxtr, TEMP, BERCAT, nsExact
from pyontutils.closed_namespaces import rdf, rdfs, owl, dc, dcterms, skos, prov

def _triples(self):
    for source in self.sources:
        for i, (label, paren_thing, abbrev, index) in enumerate(source):
            local_identifier = str(i + 1)
            iri = self.namespace[local_identifier]  # TODO load from existing
            yield from Label(labelRoot=self.root,
                            label=label,
                            #altLabel=None,
                            #synonyms=extras,
                            abbrevs=(abbrev,),
                            iri=iri,)
            if paren_thing:
                yield iri, ilx['berman/uris/readable/hasWeirdParenValue'], rdflib.Literal(paren_thing)

            continue
            # FIXME different file ...
            region_iri = ilx['berman/uris/cat/regions/' + local_identifier]
            # FIXME incorporate version in tree or no?
            # just have it be consecutive? HRM
            yield region_iri, rdf.type, owl.Class
            yield region_iri, ilxtr.hasParcellationLabel, iri  # FIXME predicate choice ...
            yield region_iri, ilxtr.isDefinedBy, BermanSrc.artifact.iri  # FIXME
            for plate_num in index:
                yield region_iri, ilxtr.appearsOnPlateNumber, rdflib.Literal(plate_num)  # FIXME generalize ...

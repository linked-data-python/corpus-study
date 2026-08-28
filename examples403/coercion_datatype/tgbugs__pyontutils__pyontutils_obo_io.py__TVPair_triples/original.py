# Extracted from tgbugs/pyontutils@cb3efcd10f : pyontutils/obo_io.py
# region: TVPair.triples (lines 550-595, stratum coercion_datatype)
# licence of the source repository: see meta.json
import rdflib
from pyontutils.core import OntId
from pyontutils.closed_namespaces import rdf, rdfs, owl, oboInOwl
obo_tag_to_ttl = {
    #'id': (lambda s, p: rdflib.URIRef(s), rdf.type, owl.Class), '%s rdf:type owl:Class ;\n',
    'name': rdfs.label,
    'def': definition,
    'acronym': NIFRID.acronym,
    'synonym': NIFRID.synonym,
    'is_a': rdfs.subClassOf,
    'xref': oboInOwl.hasDbXref,
    #'xref':

}

def triples(self, subject=None):
    if subject is None:
        subject = rdflib.BNode()

    if self.tag == 'id':
        yield id_fix(self.value), rdf.type, owl.Class

    elif self.tag in obo_tag_to_ttl:
        predicate = obo_tag_to_ttl[self.tag]
        if self.tag == 'def':
            #value = self._value.text.replace('"','\\"')
            value = self._value.text
            object = rdflib.Literal(value)

        elif self.tag == 'synonym':
            value = self._value.text.lower()
            object = rdflib.Literal(value)

        elif self.tag == 'is_a':
            if self._value.target == self._value.DANGLING:  # we dangling
                value = self._value.target_id
            else:
                value = id_fix(self._value.target.id_.value)

            object = rdflib.URIRef(value)

        elif self.tag == 'name':
            value = self.value.lower()  # capitalize only proper nouns as needed
            object = rdflib.Literal(value)

        elif self.tag == 'xref':
            value = self.value
            if '\:' in value:
                value = value.replace('\:', ':')
            try:
                object = OntId(value).URIRef
            except (OntId.UnknownPrefixError, OntId.BadCurieError) as e:
                object = rdflib.Literal(value)  # FIXME

        else:
            value = self.value
            if '\:' in value:
                value = value.replace('\:', ':')
            object = rdflib.URIRef(value)

        yield subject, predicate, object

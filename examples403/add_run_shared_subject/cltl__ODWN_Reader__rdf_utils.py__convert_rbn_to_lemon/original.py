# Extracted from cltl/ODWN_Reader@f3b8d40de1 : rdf_utils.py
# region: convert_rbn_to_lemon (lines 10-101, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
from rdflib.namespace import RDF, RDFS, XSD
from rdflib.namespace import Namespace
from rdflib import URIRef
from rdflib import Literal
from rdflib import Graph

def convert_rbn_to_lemon(senseid_to_senseobj,
                         namespace,
                         lemon,
                         major_version,
                         minor_version,
                         rbn_pos_to_lexinfo,
                         language='nld',
                         output_path=None,
                         verbose=0):

    assert language == 'nld', f'language should be nld'

    g = Graph()

    LEMON = Namespace('http://lemon-model.net/lemon#')
    DCT = Namespace('http://purl.org/dc/terms/')
    LEXINFO = Namespace('http://www.lexinfo.net/ontology/3.0/lexinfo#')

    g.bind('lemon', LEMON)
    g.bind('dct', DCT)
    g.bind('lexinfo', LEXINFO)

    lexicon_uri = f'{namespace}lexicon-{major_version}.{minor_version}'

    # update lexicon information
    lexicon_uri_obj = URIRef(lexicon_uri)

    assert LEMON.Lexicon in lemon.subjects()
    g.add((lexicon_uri_obj, RDF.type, LEMON.Lexicon))

    assert LEMON.language in lemon.subjects()
    g.add((lexicon_uri_obj, LEMON.language, Literal(language)))

    lexicon_label = f'Open Referentie Bestand Nederlands versie {major_version}.{minor_version}: nouns, verbs, and adjectives for senses with prefix c and r'
    g.add((lexicon_uri_obj, RDFS.label, Literal(lexicon_label)))

    lexicon_version = float(f'{major_version}.{minor_version}')
    g.add((lexicon_uri_obj, DCT.identifier, Literal(lexicon_version,
                                                    datatype=XSD.decimal)))

    pos_tagset = set()
    for sense_id, sense_obj in senseid_to_senseobj.items():

        le_uri = f'{lexicon_uri}-le-{sense_id}'
        leform_uri = f'{lexicon_uri}-leform-{sense_id}'
        lu_uri = f'{lexicon_uri}-lu-{sense_id}'

        # update LE information
        le_obj = URIRef(le_uri)
        assert LEMON.LexicalEntry in lemon.subjects()
        g.add((le_obj, RDF.type, LEMON.LexicalEntry))

        pos_tagset.add(sense_obj.rbn_pos)
        g.add((le_obj,
               LEXINFO.partOfSpeech,
               URIRef(rbn_pos_to_lexinfo[sense_obj.rbn_pos]))
              )

        # update LE form
        lemma = sense_obj.lemma
        le_form_obj = URIRef(leform_uri)
        g.add((le_form_obj, RDFS.isDefinedBy, le_obj))
        assert LEMON.Form in lemon.subjects()
        g.add((le_form_obj, RDF.type, LEMON.Form))
        assert LEMON.writtenRep in lemon.subjects()

        g.add((le_form_obj, LEMON.writtenRep, Literal(lemma, lang=language)))

        assert LEMON.canonicalForm in lemon.subjects()
        g.add((le_obj, LEMON.canonicalForm, le_form_obj))

        # update LU information
        lu_obj = URIRef(lu_uri)
        assert LEMON.sense in lemon.subjects()
        g.add((le_obj, LEMON.sense, lu_obj))
        assert LEMON.LexicalSense in lemon.subjects()
        g.add((lu_obj, RDF.type, LEMON.LexicalSense))
        g.add((lu_obj, DCT.identifier, Literal(sense_obj.sense_id)))
        assert LEMON.isSenseOf in lemon.subjects()
        g.add((lu_obj, LEMON.isSenseOf, le_obj))

        if sense_obj.definition is not None:
            assert LEMON.definition in lemon.subjects()
            g.add((lu_obj, LEMON.definition, Literal(sense_obj.definition,
                                                     lang=language)))

    if output_path is not None:
        g.serialize(format='turtle', destination=output_path)
        if verbose >= 1:
            print(f'written Lemon representation of RBN ({major_version}.{minor_version} in language {language}) to {output_path}')

    return g

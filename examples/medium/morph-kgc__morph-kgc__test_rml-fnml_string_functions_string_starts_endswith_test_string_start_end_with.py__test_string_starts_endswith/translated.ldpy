# Extracted from morph-kgc/morph-kgc@a2122e88bb : test/rml-fnml/string_functions/string_starts_endswith/test_string_start_end_with.py
# region: test_string_starts_endswith (lines 14-21, band medium)
# licence of the source repository: see meta.json
import os
import rdflib
import rdflib.compare
import morph_kgc

def test_string_starts_endswith():    
    mapping_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mapping.yarrrml')
    csv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'cars.csv')
    config = f'[DataSource]\nmappings:{mapping_path}\nfile_path:{csv_path}'
    rml_morph = morph_kgc.materialize(config)
    rmlmapper_goldstandard = rdflib.Graph()
    rmlmapper_goldstandard.parse(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'rmlmapperoutput.ttl'))
    assert rdflib.compare.isomorphic(rml_morph, rmlmapper_goldstandard)

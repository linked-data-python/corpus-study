# Extracted from johnjung/metadata_converters@36a81d6a97 : metadata_converters/test_ttl.py
# region: TestTTL.test_maps_chisoc_cho (lines 15-90, stratum trav_existence)
# licence of the source repository: see meta.json
from rdflib import Graph, Literal, URIRef

def test_maps_chisoc_cho(self):
    # dc:description, dc:title, or both are manditory.
    predicate_exists = []
    for predicate in (
        'http://purl.org/dc/elements/1.1/description',
        'http://purl.org/dc/elements/1.1/title'
    ):
        predicate_exists.append(
            (
                URIRef('ark:61001/b2nw3wm8552h'),
                URIRef(predicate),
                None
            ) in self.g_3404181
        )
    self.assertTrue(any(predicate_exists))

    # at least one of dc:coverage, dcterms:spatial, dc:subject,
    # dcterms:temporal, or dc:type are required. 
    predicate_exists = []
    for predicate in (
        'http://purl.org/dc/elements/1.1/coverage',
        'http://purl.org/dc/terms/spatial',
        'http://purl.org/dc/elements/1.1/subject',
        'http://purl.org/dc/terms/temporal',
        'http://purl.org/dc/elements/1.1/type'
    ):
        predicate_exists.append(
            (
                URIRef('ark:61001/b2nw3wm8552h'),
                URIRef(predicate),
                None
            ) in self.g_3404181
        )
    self.assertTrue(any(predicate_exists))

    # dc:language must appear for TEXT objects.
    self.assertTrue(
        (
            URIRef('ark:61001/b2nw3wm8552h'),
            URIRef('http://purl.org/dc/elements/1.1/language'),
            None
        ) in self.g_3404181
    )

    # edm:type must occur.
    self.assertTrue(
        (
            URIRef('ark:61001/b2nw3wm8552h'),
            URIRef('http://www.europeana.eu/schemas/edm/type'),
            None
        ) in self.g_3404181
    )

    # edm:type must be one of the following: TEXT, IMAGE, SOUND,
    # VIDEO or 3D.
    self.assertTrue(
        self.g_3404181.value(
            subject=URIRef('ark:61001/b2nw3wm8552h'),
            predicate=URIRef('http://www.europeana.eu/schemas/edm/type')
        ) in (
            Literal('3D'),
            Literal('IMAGE'),
            Literal('SOUND'),
            Literal('TEXT'),
            Literal('VIDEO')
        )
    )

    # edm:year should occur.
    self.assertTrue(
        (
            URIRef('ark:61001/b2nw3wm8552h'),
            URIRef('http://www.europeana.eu/schemas/edm/year'),
            None
        ) in self.g_3404181
    )

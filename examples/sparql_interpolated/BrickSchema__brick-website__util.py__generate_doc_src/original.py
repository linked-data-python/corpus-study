# Extracted from BrickSchema/brick-website@b9506a909d : util.py
# region: generate_doc_src (lines 124-190, stratum sparql_interpolated)
# licence of the source repository: see meta.json
def get_class_details(iri, hierarchy=[]):
    return {
        "id": f"{version}^{iri}",
        "version": version,
        "namespace": f"{version}^{get_ns(iri)}",
        "type": "class",
        "types": [
            f"{instance_type[0]}"
            for instance_type in g.query(
                f"SELECT DISTINCT ?instance_type WHERE {{ <{iri}> (owl:equivalentClass|^owl:equivalentClass)*/a ?instance_type . }}"
            )
        ],
        "name": minify(iri),
        "path": f"/ontology/{version}/classes/{minify(iri)}",
        "labels": [
            label[0]
            for label in g.query(
                f"SELECT DISTINCT ?label WHERE {{ <{iri}> (owl:equivalentClass|^owl:equivalentClass)*/rdfs:label ?label . }}"
            )
        ],
        "generatedLabel": " ".join(minify(iri).split("_")),
        "generatedAlias": get_alias(iri),
        "superclasses": [
            f"{version}^{superclass[0]}"
            for superclass in g.query(
                f"SELECT DISTINCT ?superclass WHERE {{ <{iri}> rdfs:subClassOf/(owl:equivalentClass|^owl:equivalentClass)* ?superclass . }}"
            )
        ],
        "subclasses": [
            f"{version}^{subclass[0]}"
            for subclass in g.query(
                f"SELECT DISTINCT ?subclass WHERE {{ ?subclass (owl:equivalentClass|^owl:equivalentClass)*/rdfs:subClassOf <{iri}> . }}"
            )
        ],
        "comments": [
            comment[0]
            for comment in g.query(
                f"SELECT DISTINCT ?comment WHERE {{ <{iri}> (owl:equivalentClass|^owl:equivalentClass)*/rdfs:comment ?comment . }}"
            )
        ],
        "definitions": [
            definition[0]
            for definition in g.query(
                f"SELECT DISTINCT ?definition WHERE {{ <{iri}> (owl:equivalentClass|^owl:equivalentClass)*/skos:definition ?definition . }}"
            )
        ],
        "equivalentClasses": [
            f"{version}^{klass[0]}"
            for klass in g.query(
                f"SELECT DISTINCT ?klass WHERE {{ <{iri}> (owl:equivalentClass|^owl:equivalentClass)* ?klass . FILTER (?klass != <{iri}>) . }}"
            )
        ],
        "hierarchy": hierarchy,
        "inRangeOf": [
            f"{version}^{relationship[0]}"
            for relationship in g.query(
                f"SELECT DISTINCT ?relationship WHERE {{ ?relationship rdfs:range ?range_class . <{iri}> (owl:equivalentClass|^owl:equivalentClass|rdfs:subClassOf)* ?range_class. }}"
            )
        ],
        "inDomainOf": [
            f"{version}^{relationship[0]}"
            for relationship in g.query(
                f"SELECT DISTINCT ?relationship WHERE {{ ?relationship rdfs:domain ?domain_class . <{iri}> (owl:equivalentClass|^owl:equivalentClass|rdfs:subClassOf)* ?domain_class. }}"
            )
        ],
        "shaclDetails": get_shacl_details(g, iri),
    }

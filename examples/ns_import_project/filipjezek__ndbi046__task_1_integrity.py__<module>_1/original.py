# Extracted from filipjezek/ndbi046@59b3a45240 : task_1/integrity.py
# region: <module> (lines 1-76, stratum ns_import_project)
# licence of the source repository: see meta.json
#!/usr/bin/env python3
from pathlib import Path
from rdflib import Graph
from rdflib.namespace import RDF, SKOS, QB, XSD, OWL
from cube_lib.namespaces import RDFS

import population
import care_providers


def main():
    for src, factory in (
        ('data/population.csv', population.create_cube),
        ('data/care_providers.csv', care_providers.create_cube)
    ):
        with open(src, 'r', encoding='UTF-8') as stream:
            print('\n' + src)
            test_cube(factory(stream))


def bind_namespaces(cube: Graph):
    cube.bind("rdf", RDF)
    cube.bind("rdfs", RDFS)
    cube.bind("skos", SKOS)
    cube.bind("qb", QB)
    cube.bind("xsd", XSD)
    cube.bind("owl", OWL)


def test_cube(cube: Graph):
    bind_namespaces(cube)
    for file in Path('./queries').glob('*.sparql'):
        if file.name.endswith('.inst.sparql'):
            continue

        print(file.stem, end=' ')
        if file.name.endswith('.templ.sparql'):
            instances = load_template_queries(file, cube)
            if len(instances) == 0:
                print(pretty_bool(False))
            else:
                all_ok = all(bool(cube.query(i)) for i in instances)
                print(pretty_bool(all_ok))
        else:
            res = cube.query(load_query(file))
            print(pretty_bool(res))


def load_query(path: Path):
    with open(str(path), 'r', encoding='UTF-8') as stream:
        return stream.read()


def load_template_queries(path: Path, cube: Graph):
    inst_query = load_query(path.with_name(
        path.name.replace('.templ.sparql', '.inst.sparql')))
    templ_query = load_query(path)

    res = cube.query(inst_query)
    instances = []
    for row in res:
        repl = templ_query
        for key in row.asdict():
            repl = repl.replace('$' + key, row[key])
        instances.append(repl)
    return instances


def pretty_bool(val):
    if (bool(val)):
        return '\033[91mFAILED\033[0m'
    return '\033[92mOK\033[0m'


if __name__ == '__main__':
    main()

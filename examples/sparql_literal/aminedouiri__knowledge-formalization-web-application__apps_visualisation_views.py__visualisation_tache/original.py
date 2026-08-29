# Extracted from aminedouiri/knowledge-formalization-web-application@0a8007ff46 : apps/visualisation/views.py
# region: visualisation_tache (lines 123-166, stratum sparql_literal)
# licence of the source repository: see meta.json
import rdflib 
import os

def visualisation_tache():

    g = rdflib.Graph()
    g.parse("apps/connaissance/static/viz-onto/viz_tache.ttl")
    query = """
    SELECT ?tache
    WHERE {
        ?tache a :Tache .
    }"""
    qres = g.query(query)
    taches = []

    for row in qres:
        tache = str(row.tache).replace('http://dig.isi.edu/', '')
        taches.append(tache)

    nbr=len(taches)
    nbr = nbr + 1
    nbr = str(nbr)

    file = open("apps/connaissance/static/viz-onto/viz_tache.ttl", "a")

    a = '\n:tache'+ nbr +' a :Tache ;\n'
    a +='\t' + ':nom ' + '"'+nom_tache+'"' + ' ;\n' + '\t' +':type ' + '"'+type_tache+'"' + " ;\n"
    a +='\t' + ':condition ' + '"'+ind_condition+'"' + ' ;\n'
    a += '\t' + ':objectif ' + '"'+ind_objectif+'"' + ' .\n'

    file.write(a)
    file.close()

    filewrite = open("tache"+nbr+".ttl", "w")

    filewrite.write("@prefix : <http://dig.isi.edu/> .\n"+
                    "@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"+
                    "@prefix owl:   <http://www.w3.org/2002/07/owl#> .\n"+
                    "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n")

    filewrite.write(a)
    filewrite.close()

    os.system("python apps/visualisation/ontology_viz.py -o tache"+nbr+".dot tache"+nbr+".ttl -O apps/connaissance/static/ontologie-data/ontology_tache.ttl")
    os.remove("tache"+nbr+".ttl")
    os.system("dot -Tpng -o "+ "apps/connaissance/static/formalismes/tache/tache" +nbr+".png tache"+nbr+".dot")
    os.remove("tache"+nbr+".dot")

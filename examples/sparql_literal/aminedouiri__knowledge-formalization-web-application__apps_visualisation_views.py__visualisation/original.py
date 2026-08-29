# Extracted from aminedouiri/knowledge-formalization-web-application@0a8007ff46 : apps/visualisation/views.py
# region: visualisation (lines 9-120, stratum sparql_literal)
# licence of the source repository: see meta.json
from django.shortcuts import render
import rdflib 
from apps.connaissance.models import Connaissance
from apps.commentaire.models import Commentaire

def visualisation(request):
    #Tache 

    g_tache = rdflib.Graph()
    g_tache.parse("apps/connaissance/static/viz-onto/viz_tache.ttl")
    query_tache = """
    SELECT ?tache
    WHERE {
        ?tache a :Tache .
    }"""
    qres_tache = g_tache.query(query_tache)
    taches = []

    for row in qres_tache:
        tache = str(row.tache).replace('http://dig.isi.edu/', '')
        taches.append(tache)


    #Activite
    g_activite = rdflib.Graph()
    g_activite.parse("apps/connaissance/static/viz-onto/viz_activite.ttl")
    query_activite = """
    SELECT ?activite
    WHERE {
        ?activite a :Activite .
    }"""
    qres_activite = g_activite.query(query_activite)
    activites = []

    for row in qres_activite:
        activite = str(row.activite).replace('http://dig.isi.edu/', '')
        activites.append(activite)

    #Historique
    g_historique = rdflib.Graph()
    g_historique.parse("apps/connaissance/static/viz-onto/viz_historique.ttl")
    query_historique = """
    SELECT ?generation
    WHERE {
        ?generation a :Generation .
    }"""
    qres_generation = g_historique.query(query_historique)
    generations = []

    for row in qres_generation:
        generation = str(row.generation).replace('http://dig.isi.edu/', '')
        generations.append(generation)

    #Phenomenes
    g_phenomene = rdflib.Graph()
    g_phenomene.parse("apps/connaissance/static/viz-onto/viz_phenomene.ttl")
    query_phenomene = """
    SELECT ?phenomene
    WHERE {
        ?phenomene a :Phenomene_Metier .
    }"""
    qres_phenomene = g_phenomene.query(query_phenomene)
    phenomenes = []

    for row in qres_phenomene:
        phenomene = str(row.phenomene).replace('http://dig.isi.edu/', '')
        phenomenes.append(phenomene)


    #Domaines
    g_domaine = rdflib.Graph()
    g_domaine.parse("apps/connaissance/static/viz-onto/viz_domaine.ttl")
    query_domaine = """
    SELECT ?domaine
    WHERE {
        ?domaine a :Domaine .
    }"""
    qres_domaine = g_domaine.query(query_domaine)
    domaines = []

    for row in qres_domaine:
        domaine = str(row.domaine).replace('http://dig.isi.edu/', '')
        domaines.append(domaine)

    #Strategique
    g_strategie = rdflib.Graph()
    g_strategie.parse("apps/connaissance/static/viz-onto/viz_strategie.ttl")
    query_strategie = """
    SELECT ?strategie
    WHERE {
        ?strategie a :Strategie .
    }"""
    qres_strategie = g_strategie.query(query_strategie)
    strategies = []

    for row in qres_strategie:
        strategie = str(row.strategie).replace('http://dig.isi.edu/', '')
        strategies.append(strategie)

    print(strategies)

    connaissanceNotification = Connaissance.objects.filter(status_vue=False).count()
    commentaires = Commentaire.objects.all()
    connaissanceNotification += commentaires.count()

    context = {
        'taches': taches,
        'activites': activites,
        'generations': generations,
        'phenomenes_metier': phenomenes,
        'domaines':domaines,
        'strategies':strategies,
        'connaissanceNotification': connaissanceNotification,
    }


    return render(request, 'visualisation/visualisation.html', context)

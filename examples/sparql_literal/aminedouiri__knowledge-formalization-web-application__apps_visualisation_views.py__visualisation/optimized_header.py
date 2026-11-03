# Extracted from aminedouiri/knowledge-formalization-web-application@0a8007ff46 : apps/visualisation/views.py
# region: visualisation (lines 9-120, stratum sparql_literal)
# licence of the source repository: see meta.json
# Context shim: `render`/`Connaissance`/`Commentaire` come from ./context.py
# (see meta.json), a stand-in for Django and the sibling apps that are not
# available outside the project. `visualisation` also gained six defaulted
# path parameters, one per ontology file it parses: the function otherwise
# takes no graph and reads six hardcoded paths, so this is the 163-region
# case of restoring a binding the extracted region cannot otherwise carry
# (design record corpus/403 s6). Called with no arguments it behaves exactly
# as before.
import rdflib
from context import render, Connaissance, Commentaire

def visualisation(request,
                   tache_path="apps/connaissance/static/viz-onto/viz_tache.ttl",
                   activite_path="apps/connaissance/static/viz-onto/viz_activite.ttl",
                   historique_path="apps/connaissance/static/viz-onto/viz_historique.ttl",
                   phenomene_path="apps/connaissance/static/viz-onto/viz_phenomene.ttl",
                   domaine_path="apps/connaissance/static/viz-onto/viz_domaine.ttl",
                   strategie_path="apps/connaissance/static/viz-onto/viz_strategie.ttl"):
    taches, activites, generations, phenomenes, domaines, strategies = (
        [str(row[0]).replace('http://dig.isi.edu/', '')
         for row in rdflib.Graph().parse(path).query("SELECT ?x WHERE { ?x a :%s }" % cls)]
        for path, cls in ((tache_path, "Tache"), (activite_path, "Activite"),
                          (historique_path, "Generation"), (phenomene_path, "Phenomene_Metier"),
                          (domaine_path, "Domaine"), (strategie_path, "Strategie")))
    print(strategies)

    connaissanceNotification = (Connaissance.objects.filter(status_vue=False).count()
                                + Commentaire.objects.all().count())

    return render(request, 'visualisation/visualisation.html', {
        'taches': taches,
        'activites': activites,
        'generations': generations,
        'phenomenes_metier': phenomenes,
        'domaines':domaines,
        'strategies':strategies,
        'connaissanceNotification': connaissanceNotification,
    })

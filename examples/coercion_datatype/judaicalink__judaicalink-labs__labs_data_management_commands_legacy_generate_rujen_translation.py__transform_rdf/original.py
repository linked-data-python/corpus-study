# Extracted from judaicalink/judaicalink-labs@b683b52eaa : labs/data/management/commands/legacy/generate_rujen_translation.py
# region: transform_rdf (lines 70-89, stratum coercion_datatype)
# licence of the source repository: see meta.json
from ._dataset_command import DatasetCommand, jlo, skos, log, error
import rdflib
from googletrans import Translator
import re
trans_cached = {}
src_lang = "ru"

def transform_rdf(graph, ingraph):
    global translator
    query = "SELECT ?s ?o WHERE {?s <" + str(prop) + "> ?o .}"
    res = ingraph.query(query)
    for triple in res:
        s = str(triple["s"])
        if s in trans_cached:
            trans = trans_cached[s].strip()
            log.info(f"Added translation (cached): {s}: {trans[:20]}")
        else:
            trans = translator.translate(triple["o"], src=src_lang, dest=dest_lang)
            log.info(f"Added translation: {s}: {trans.text.strip()[:20]} {trans.src} - {trans.dest}")
            if trans.src=="ru" and re.search('[а-яА-Я]', trans.text.strip()):
                error.info(f"Cyrillic in translation: {s}")
            if trans.src=="ru":
                trans_cached[s] = trans.text.strip()
            else:
                log.info("Translation does not work anymore, getting no translation. I use a new instance.")
                translator = Translator()
        graph.add((triple["s"], prop, rdflib.Literal(trans, dest_lang)))

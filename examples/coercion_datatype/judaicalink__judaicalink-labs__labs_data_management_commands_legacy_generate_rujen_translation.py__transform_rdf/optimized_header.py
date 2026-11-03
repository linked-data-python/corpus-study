# Extracted from judaicalink/judaicalink-labs@b683b52eaa : labs/data/management/commands/legacy/generate_rujen_translation.py
# region: transform_rdf (lines 70-89, stratum coercion_datatype)
# licence of the source repository: see meta.json
from context_shim import log, error, Translator, configure_task  # context shim, see meta.json
import rdflib
import re
translator = Translator()
trans_cached = {}
src_lang = "ru"

def transform_rdf(graph, ingraph):
    global translator
    for subject, label in ingraph.subject_objects(prop):
        s = str(subject)
        if s in trans_cached:
            trans = trans_cached[s].strip()
            log.info(f"Added translation (cached): {s}: {trans[:20]}")
        else:
            trans = translator.translate(label, src=src_lang, dest=dest_lang)
            text = trans.text.strip()
            log.info(f"Added translation: {s}: {text[:20]} {trans.src} - {trans.dest}")
            if trans.src=="ru":
                if re.search('[а-яА-Я]', text):
                    error.info(f"Cyrillic in translation: {s}")
                trans_cached[s] = text
            else:
                log.info("Translation does not work anymore, getting no translation. I use a new instance.")
                translator = Translator()
        graph.add((subject, prop, rdflib.Literal(trans, dest_lang)))


# Binding restoration (identical on both sides, see meta.json): `prop` and
# `dest_lang` are module globals that the source's configure_task() sets
# before transform_rdf() runs; `run` does the same for one task and hands
# back the graph the region wrote to.
def run(task, ingraph):
    configure_task(task, globals())
    graph = rdflib.Graph()
    transform_rdf(graph, ingraph)
    return graph

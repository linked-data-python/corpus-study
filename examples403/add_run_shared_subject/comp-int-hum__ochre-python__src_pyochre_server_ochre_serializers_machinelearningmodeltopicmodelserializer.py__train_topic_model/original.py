# Extracted from comp-int-hum/ochre-python@8392c11405 : src/pyochre/server/ochre/serializers/machinelearningmodeltopicmodelserializer.py
# region: train_topic_model (lines 153-267, stratum add_run_shared_subject)
# licence of the source repository: see meta.json
import random
import os.path
import re
import os
import os.path
from django.conf import settings
from gensim.models import LdaModel
from gensim.corpora import Dictionary
from rdflib import Graph, BNode, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD, Namespace
from pyochre.utils import ochrequery as OQ
OCHRE = Namespace(settings.OCHRE_NAMESPACE)
logger = logging.getLogger(__name__)

try:
    for binding in primarysource.query(OQ(input_query_string)):
        if binding.get("word"):
            doc = str(binding.get("doc"))
            word = binding.get("word").value
            docs[doc] = docs.get(doc, [])
            word = word.lower() if lowercase else word
            if word not in stopwords and len(word) >= minimum_token_length:
                docs[doc].append(word)
        else:
            doc = str(binding.get("doc"))
            mid = binding.get("mid").value
            docs[doc] = docs.get(doc, [])
            text = ms.retrieve(mid)["content"]
            for m in re.finditer(word_regex, text.decode("utf-8")):
                word = m.group(0)
                word = word.lower() if lowercase else word
                if word not in stopwords and len(word) >= minimum_token_length:
                    docs[doc].append(word)

    subdocs = []
    for doc in docs.values():
        while len(doc) > 0:
            subdocs.append(doc[0:maximum_context_tokens])
            doc = doc[maximum_context_tokens:]
    random.shuffle(subdocs)
    logger.info(
        "Loading at most %d subdocuments out of %d",
        maximum_documents,
        len(subdocs),
    )
    subdocs = subdocs[:maximum_documents]
    logger.info("Loaded %d subdocuments", len(subdocs))
    dictionary = Dictionary(subdocs)
    dictionary.filter_extremes(
        no_below=minimum_occurrence,
        no_above=maximum_proportion,
        keep_n=maximum_vocabulary_size,            
    )
    corpus = [dictionary.doc2bow(subdoc) for subdoc in subdocs]
    el = EpochLogger(passes)
    topic_model = LdaModel(
        corpus=corpus,
        id2word=dictionary,
        num_topics=topic_count,
        alpha="auto",
        eta="auto",
        iterations=iterations,
        passes=passes,
        random_state=random_seed,
        eval_every=None,
        #callbacks=[el],
    )
    mar_path = os.path.join(settings.TEMP_ROOT, "model_{}.mar".format(model.id))
    sig_path = os.path.join(settings.TEMP_ROOT, "sig_{}.ttl".format(model.id))
    prop_path = os.path.join(settings.TEMP_ROOT, "prop_{}.ttl".format(model.id))
    try:
        with open(sig_path, "wt") as ofd:
            ofd.write(signature_graph.skolemize().serialize(format="turtle"))
        create_topic_model_mar(
            topic_model,
            name,
            mar_path,
            lowercase,
            word_regex,
            stopwords
        )
        with open(mar_path, "rb") as mar, open(sig_path, "rb") as sig:
            files = {
                "mar_file" : mar,
                "signature_file" : sig,
            }
            model.save(**files)

        dists = topic_model.show_topics(                
            num_topics=topic_count,
            num_words=len(dictionary.token2id),
            formatted=False
        )

        g = Graph()
        word_uris = {}
        for word, _ in dists[0][1]:
            word_uris[word] = BNode()
            g.add((word_uris[word], OCHRE["hasLabel"], Literal(word)))
            g.add((word_uris[word], OCHRE["instanceOf"], OCHRE["Word"]))
        for topic, dist in dists:
            topic_uri = BNode()
            g.add((topic_uri, OCHRE["hasOrdinal"], Literal(topic)))
            g.add((topic_uri, OCHRE["hasLabel"], Literal("Topic #{}".format(topic))))
            g.add((topic_uri, OCHRE["instanceOf"], OCHRE["CategoricalDistribution"]))
            for word, prob in dist:
                occ_uri = BNode()
                g.add((occ_uri, OCHRE["hasProbability"], Literal(prob, datatype=XSD.float)))
                g.add((occ_uri, OCHRE["partOf"], topic_uri))
                g.add((occ_uri, OCHRE["partOf"], word_uris[word]))
                g.add((occ_uri, OCHRE["instanceOf"], OCHRE["Probability"]))
        with open(prop_path, "wt") as ofd:
            ofd.write(g.skolemize().serialize(format="turtle"))
        with open(mar_path, "rb") as mar, open(sig_path, "rb") as sig, open(prop_path, "rb") as prop:
            files = {
                "properties_file" : prop
            }
            model.save(**files)
    except Exception as e:
        raise e
    finally:
        os.remove(mar_path)
        os.remove(sig_path)
        os.remove(prop_path)        
except Exception as e:        
    model.state = model.ERROR
    model.message = "{}".format(e)
    model.delete()
    raise e

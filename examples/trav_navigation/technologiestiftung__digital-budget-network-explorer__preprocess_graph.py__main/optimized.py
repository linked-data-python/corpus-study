# Extracted from technologiestiftung/digital-budget-network-explorer@a2c69bf9f4 : preprocess_graph.py
# region: main (lines 249-353, stratum trav_navigation)
# licence of the source repository: see meta.json
from rdflib import Graph, Namespace, RDF
from rdflib.namespace import SKOS, OWL, DCTERMS, RDFS

# Test harness only (see meta.json): binds the input graph, BASE, the
# string helpers and the accumulators `main()` builds before reaching this
# region, so the extracted statements run standalone. Added identically to
# original.py and translated.ldpy.
from shim import BASE, local_name, first_label, get_top_level, extract_phrases, build_fixture

(g, keywords, concept_labels, bereiche, klassen, hauptgruppen,
 hauptfunktionen, jahre, titel_beschreibung, posten) = build_fixture()

DH = Namespace(BASE + "ontology#")
SCHEMA = Namespace("https://schema.org/")
KEYWORD_PREFIX = BASE + "keyword/"

for s in g.subjects(RDF.type, DH.Haushaltsposten):
    kw = [local_name(o) for o in g.objects(s, DCTERMS.subject) if str(o).startswith(KEYWORD_PREFIX)]

    ep_obj = g.value(s, DH.einzelplan)
    ep = local_name(ep_obj) if ep_obj is not None else None

    ber_obj = g.value(s, DH.bereich)
    ber = None
    if ber_obj is not None:
        ber = local_name(ber_obj)
        bereiche.setdefault(ber, first_label(g, ber_obj) or ber)

    kl_obj = g.value(s, DH.digiKlasse)
    kl = None
    if kl_obj is not None:
        kl = local_name(kl_obj)
        # "Nicht digital" (Klasse 0) komplett ausschliessen
        if kl == "0":
            continue
        klassen.setdefault(kl, first_label(g, kl_obj) or kl)

    def top_level(pred, registry):
        obj = g.value(s, pred)
        if obj is None:
            return None
        uri = get_top_level(str(obj))
        name = local_name(uri)
        registry.setdefault(name, concept_labels.get(uri, name))
        return name

    hg = top_level(DH.gruppe, hauptgruppen)
    hf = top_level(DH.funktion, hauptfunktionen)

    jahr_obj = g.value(s, DH.jahr)
    jahr = None
    if jahr_obj is not None:
        try:
            jahr = int(str(jahr_obj)[:4])
            jahre.add(jahr)
        except ValueError:
            pass

    titel_obj = g.value(s, DCTERMS.isPartOf)
    t_id = local_name(titel_obj) if titel_obj is not None else None

    desc = g.value(s, SCHEMA.description)
    desc_text = str(desc) if desc else ""
    phrases = extract_phrases(desc_text) if desc else []

    # Store full description text for titel (first posten wins)
    if t_id and desc_text:
        titel_beschreibung.setdefault(t_id, desc_text)

    # Ordne die gefundenen Phrasen den Keywords des Postens zu
    # Einfacher Heuristik: Eine Phrase gehört zu einem Keyword, 
    # wenn der Label des Keywords als Teilstring in der Phrase vorkommt.
    kw_phrases = {}
    for k in kw:
        lbl = keywords.get(k, {}).get("label", "").lower()
        if not lbl: continue
        matched = [p for p in phrases if lbl in p.lower() or k.lower() in p.lower()]
        if matched:
            kw_phrases[k] = list(set(matched)) # deduplicate

    def num(pred):
        try:
            return round(float(g.value(s, pred)), 3)
        except (TypeError, ValueError):
            return None

    rec = {
        "t": t_id,
        "kw": kw,
        "phrases": kw_phrases,
        "ep": ep,
        "jahr": jahr,
        "ber": ber,
        "kl": kl,
        "hg": hg,
        "hf": hf,
        "soll": num(DH.soll),
        "ist": num(DH.ist),
        "digW": num(DH.istDigitalWeit),
        "sollEng": num(DH.sollDigitalEng),
        "istEng": num(DH.istDigitalEng),
    }

    # Titel mit SOLL-Budget = 0 oder fehlendem Budget direkt herausfiltern
    if not rec["soll"] or rec["soll"] <= 0:
        continue

    posten.append(rec)

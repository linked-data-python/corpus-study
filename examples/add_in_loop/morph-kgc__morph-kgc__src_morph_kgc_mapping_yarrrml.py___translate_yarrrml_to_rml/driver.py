"""Validation driver for morph-kgc__morph-kgc__src_morph_kgc_mapping_yarrrml.py___translate_yarrrml_to_rml.

The region is a bare for-loop STATEMENT, not a function: it reads three
free names (``yarrrml_mapping``, ``mapping_graph``, ``tm_id_to_norm_tm_ids``)
that a caller elsewhere in the source module supplies. ``rdfeval.harness``'s
generic ``run_pair`` cannot inject those before exec'ing the script, so this
driver seeds them itself and, for each case, runs both versions on a fresh
``rdflib.Graph()`` and compares (a) what the run raised (exception type and
message: the region has two ``raise ValueError`` and several KeyError/
TypeError paths the real caller can reach) and (b) the resulting graph by
isomorphism, the PARTIAL graph included when the run raised.

Case 0 is the original ``shim.make_fixture()`` mapping.  The others, one
branch each, use the types the real repository passes (YAML-loaded dicts,
condition parameters as lists, ``tm_id_to_norm_tm_ids`` values as sets, see
``_translate_yarrrml_to_rml`` and ``_normalize_*`` in yarrrml.py); each term
map is written so that two different wrong IRIs or objects cannot give the
same graph:

* subjects: a template string (and ``''``, falsy), a value dict, a function
  dict, ``quoted`` with two triples maps, ``quotedNonAsserted`` (its
  ``rdf:type rml:NonAssertedTriplesMap`` triple on every referenced map),
  ``quoted`` winning over ``quotedNonAsserted`` and over ``function``, a
  subject of neither str nor dict type (None, list), a dict without
  ``value`` (KeyError), an absent ``subjects`` (implicit blank node);
* subjects condition: ``str1`` only, ``str2`` only, both, a third parameter
  name that is neither, an empty parameter list, a non-string value (TypeError)
  at each of the two sites and each of ``str1``/``str2``;
* subject term type: ``iri``, ``blanknode``, ``literal`` and ``IRI`` (the two
  ``ValueError`` of the subject site, with message), none;
* graphs: a template string, ``''``, ``0``;
* predicateobjects: the three positions ``predicates``/``objects``/``graphs``
  present together (so the property pairing predicateMap/objectMap/graphMap
  is observed), each of str, ``''``, value dict, function dict, ``mappings``
  (one-element set; unknown key KeyError; empty set IndexError), ``quoted``,
  ``quotedNonAsserted``, both, empty referenced set, and precedence between
  the branches (function over mappings over quoted over value);
* after the dict branches, at the predicateobjects site: condition (str1,
  str2, neither, both), ``language`` (and ``''``), ``datatype``, ``type``
  ``iri``/``literal``/``blanknode`` and the invalid one (ValueError), and the
  precedence language > datatype > type;
* a position of neither str nor dict type, an empty ``predicateobjects``, a
  missing ``sources``, a mapping id other than the first (several loop
  iterations in one graph).
"""
import copy
import json
import sys
import traceback
from pathlib import Path

import rdflib

from rdfeval.harness import graphs_isomorphic
from shim import make_fixture

SRC = {'access': 'data.csv'}


def _m(**kw):
    """One YARRRML mapping with a default source."""
    kw.setdefault('sources', dict(SRC))
    return kw


def _one(mapping, ids=None):
    """A case with one mapping 'tm' and optional triples-map ids."""
    base = {'tmA': {'tmA'}, 'tmB': {'tmB1', 'tmB2'}, 'tmC': {'tmC'},
            'tmE': set()}
    if ids:
        base.update(ids)
    return {'mappings': {'tm': mapping}}, base


def _po(**kw):
    return _m(subjects='$(id)', predicateobjects=kw)


def _cases():
    cases = [("make_fixture", *make_fixture())]

    def add(label, mapping, ids=None):
        cases.append((label, *_one(mapping, ids)))

    # ---- sources and subjects -------------------------------------------
    add("subject template", _m(subjects='$(id)'))
    add("subject empty string", _m(subjects=''))
    add("subject none", _m(subjects=None))
    add("subject list", _m(subjects=['x']))
    add("subject value dict", _m(subjects={'value': 'http://ex.org/s'}))
    add("subject dict no value", _m(subjects={}))
    add("subject function", _m(subjects={
        'function': 'fn:f', 'parameters': [{'parameter': 'p', 'value': '$(x)'}]}))
    add("subject quoted", _m(subjects={'quoted': 'tmB'}))
    add("subject quoted empty", _m(subjects={'quoted': 'tmE'}))
    add("subject quoted unknown", _m(subjects={'quoted': 'nope'}))
    add("subject quotedNonAsserted", _m(subjects={'quotedNonAsserted': 'tmB'}))
    add("subject quotedNonAsserted empty", _m(subjects={'quotedNonAsserted': 'tmE'}))
    add("subject quoted over NA", _m(subjects={'quoted': 'tmA', 'quotedNonAsserted': 'tmC'}))
    add("subject quoted over function", _m(subjects={'quoted': 'tmA', 'function': 'f'}))
    add("subject NA over function", _m(subjects={'quotedNonAsserted': 'tmA', 'function': 'f'}))
    add("subject function over value", _m(subjects={'function': 'f', 'value': 'http://ex.org/v'}))
    add("subject no sources", {'subjects': '$(id)'})
    add("sources empty", _m(subjects='$(id)', sources={}))
    add("no subjects", _m())
    add("no subjects but predicateobjects", _m(predicateobjects={'objects': 'http://ex.org/o'}))
    # ---- subject condition ----------------------------------------------
    cond = lambda *ps: _m(subjects={'value': '$(id)', 'condition': {'parameters': list(ps)}})
    add("subject cond str1", cond(['str1', '$(abc)']))
    add("subject cond str2", cond(['str2', '$(xyz)']))
    add("subject cond both", cond(['str1', '$(abc)'], ['str2', '$(xyz)']))
    add("subject cond tuples", cond(('str1', '$(abc)'), ('str2', '$(xyz)')))
    add("subject cond other", cond(['other', '$(abc)'], ['str1', '$(q)']))
    add("subject cond empty", cond())
    add("subject cond str1 not str", cond(['str1', 7]))
    add("subject cond str2 not str", cond(['str2', None]))
    add("subject cond str2 not str after str1", cond(['str1', '$(ok)'], ['str2', 7]))
    add("subject cond no parameters key", _m(subjects={'value': '$(id)', 'condition': {}}))
    add("subject cond on quoted", _m(subjects={
        'quoted': 'tmA', 'condition': {'parameters': [['str1', '$(abc)']]}}))
    # ---- subject term type ----------------------------------------------
    for t in ('iri', 'blanknode', 'literal', 'IRI', ''):
        add(f"subject type {t!r}", _m(subjects={'value': '$(id)', 'type': t}))
    add("subject type on quoted", _m(subjects={'quoted': 'tmA', 'type': 'blanknode'}))
    add("subject cond then bad type", _m(subjects={
        'value': '$(id)', 'condition': {'parameters': [['str1', '$(abc)']]},
        'type': 'literal'}))
    # ---- graphs ---------------------------------------------------------
    add("graphs template", _m(subjects='$(id)', graphs='http://ex.org/g'))
    add("graphs empty", _m(subjects='$(id)', graphs=''))
    add("graphs zero", _m(subjects='$(id)', graphs=0))
    add("graphs without subjects", _m(graphs='$(g)'))
    # ---- predicateobjects -----------------------------------------------
    add("po empty", _m(subjects='$(id)', predicateobjects={}))
    add("po unrelated key", _po(inversepredicates='http://ex.org/i'))
    add("po three strs", _po(predicates='http://ex.org/p', objects='$(o)',
                             graphs='http://ex.org/g'))
    add("po empty strs", _po(predicates='', objects='', graphs=''))
    add("po not str nor dict", _po(predicates=None, objects=['x'], graphs=3))
    add("po three dicts", _po(
        predicates={'value': 'http://ex.org/p'},
        objects={'value': '$(o)'},
        graphs={'value': 'http://ex.org/g'}))
    add("po dict no value", _po(objects={}))
    add("po function", _po(
        predicates={'function': 'fn:p', 'parameters': [{'parameter': 'a', 'value': '$(x)'}]},
        objects={'function': 'fn:o', 'type': 'iri'}))
    add("po function bad type", _po(objects={'function': 'fn:o', 'type': 'nope'}))
    add("po function over mappings", _po(objects={'function': 'fn:o', 'mappings': 'tmA'}))
    add("po function with decorations", _po(objects={
        'function': 'fn:o', 'condition': {'parameters': [['str1', '$(abc)']]},
        'language': 'fr'}))
    add("po mappings", _po(predicates={'mappings': 'tmA'}, objects={'mappings': 'tmC'},
                           graphs={'mappings': 'tmA'}))
    add("po mappings unknown", _po(objects={'mappings': 'nope'}))
    add("po mappings empty set", _po(objects={'mappings': 'tmE'}))
    add("po mappings over quoted", _po(objects={'mappings': 'tmA', 'quoted': 'tmC'}))
    add("po mappings over value", _po(objects={'mappings': 'tmA', 'value': 'http://ex.org/v'}))
    add("po quoted", _po(predicates={'quoted': 'tmB'}, objects={'quoted': 'tmA'},
                         graphs={'quoted': 'tmC'}))
    add("po quoted empty", _po(objects={'quoted': 'tmE'}))
    add("po quoted unknown", _po(objects={'quoted': 'nope'}))
    add("po quotedNonAsserted", _po(predicates={'quotedNonAsserted': 'tmB'},
                                    objects={'quotedNonAsserted': 'tmA'},
                                    graphs={'quotedNonAsserted': 'tmC'}))
    add("po quotedNonAsserted empty", _po(objects={'quotedNonAsserted': 'tmE'}))
    add("po quotedNonAsserted unknown", _po(objects={'quotedNonAsserted': 'nope'}))
    add("po quoted over NA", _po(objects={'quoted': 'tmA', 'quotedNonAsserted': 'tmC'}))
    add("po quoted over value", _po(objects={'quoted': 'tmA', 'value': 'http://ex.org/v'}))
    add("po NA over value", _po(objects={'quotedNonAsserted': 'tmA', 'value': 'http://ex.org/v'}))
    # ---- decorations of a dict term map ---------------------------------
    deco = lambda **kw: _po(objects=dict(value='http://ex.org/v', **kw))
    add("po cond str1", deco(condition={'parameters': [['str1', '$(abc)']]}))
    add("po cond str2", deco(condition={'parameters': [['str2', '$(xyz)']]}))
    add("po cond both", deco(condition={'parameters': [['str1', '$(abc)'], ['str2', '$(xyz)']]}))
    add("po cond other", deco(condition={'parameters': [['other', '$(abc)'], ['str2', '$(q)']]}))
    add("po cond empty", deco(condition={'parameters': []}))
    add("po cond str1 not str", deco(condition={'parameters': [['str1', 7]]}))
    add("po cond str2 not str", deco(condition={'parameters': [['str2', None]]}))
    add("po cond on quoted", _po(objects={'quoted': 'tmA',
                                          'condition': {'parameters': [['str1', '$(abc)'], ['str2', '$(xyz)']]}}))
    add("po cond on mappings", _po(objects={'mappings': 'tmA',
                                            'condition': {'parameters': [['str2', '$(xyz)']]}}))
    add("po language", deco(language='fr'))
    add("po language empty", deco(language=''))
    add("po language over datatype", deco(language='fr', datatype='http://ex.org/dt', type='iri'))
    add("po datatype", deco(datatype='http://ex.org/dt'))
    add("po datatype over type", deco(datatype='http://ex.org/dt', type='literal'))
    for t in ('iri', 'literal', 'blanknode', 'nope', 'IRI', ''):
        add(f"po type {t!r}", deco(type=t))
    add("po type on mappings", _po(objects={'mappings': 'tmA', 'type': 'literal'}))
    add("po language on quoted", _po(objects={'quoted': 'tmA', 'language': 'en'}))
    add("po decorations in three positions", _po(
        predicates={'value': 'http://ex.org/p', 'type': 'iri'},
        objects={'value': '$(o)', 'language': 'en'},
        graphs={'value': 'http://ex.org/g', 'datatype': 'http://ex.org/dt'}))
    # ---- several mappings in one run ------------------------------------
    cases.append(("two mappings", {'mappings': {
        'tmA': _m(subjects='$(id)', predicateobjects={'objects': '$(o)'}),
        'tmB': _m(subjects={'quoted': 'tmA', 'type': 'iri'}, graphs='http://ex.org/g'),
        'tmC': _m(),
    }}, {'tmA': {'tmA'}, 'tmB': {'tmB'}, 'tmC': {'tmC'}}))
    cases.append(("bad second mapping", {'mappings': {
        'tmA': _m(subjects='$(id)'),
        'tmB': _m(subjects={'value': '$(id)', 'type': 'nope'}),
        'tmC': _m(subjects='$(never)'),
    }}, {'tmA': {'tmA'}, 'tmB': {'tmB'}, 'tmC': {'tmC'}}))
    cases.append(("no mappings", {'mappings': {}}, {}))
    return cases


def _compile(path: Path):
    if path.suffix == ".ldpy":
        from ldpy.transpiler import transpile
        r = transpile(path.read_text(), filename=str(path))
        return compile(r.code, str(path), "exec")
    return compile(path.read_text(), str(path), "exec")


def _run(code, path, case):
    """(raised, graph): what the region raised and the graph it left."""
    _, yarrrml_mapping, tm_ids = case
    mapping_graph = rdflib.Graph()
    ns: dict = {
        "__name__": "__mod__",
        "__file__": str(path),
        "yarrrml_mapping": copy.deepcopy(yarrrml_mapping),
        "mapping_graph": mapping_graph,
        "tm_id_to_norm_tm_ids": copy.deepcopy(tm_ids),
    }
    raised = None
    try:
        exec(code, ns)
    except Exception as e:  # noqa: BLE001 - compared
        raised = (type(e).__name__, str(e))
    return raised, ns["mapping_graph"]


def main() -> None:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "statement:seeded-globals+isomorphism+raises",
                     "diffs": [], "error": None}
    try:
        from rdfeval.harness import sides_from_env
        left, right = sides_from_env()
        verdict["sides"] = [left, right]
        p_o, p_t = ex_dir / left, ex_dir / right
        c_o, c_t = _compile(p_o), _compile(p_t)
        diffs: list[str] = []
        raised_any = False
        for i, case in enumerate(_cases()):
            r_o, g_o = _run(c_o, p_o, case)
            r_t, g_t = _run(c_t, p_t, case)
            raised_any = raised_any or r_o is not None
            if r_o != r_t:
                diffs.append(f"case {i} ({case[0]}): raised {r_o!r} vs {r_t!r}")
            if not graphs_isomorphic(g_o, g_t):
                diffs.append(f"case {i} ({case[0]}): mapping_graph not "
                             f"isomorphic ({len(g_o)} vs {len(g_t)} triples)")
        if not raised_any:
            diffs.append("no case raised: the error paths are not exercised")
    except Exception:
        verdict["error"] = traceback.format_exc(limit=8)
        print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
        return

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)


if __name__ == "__main__":
    main()

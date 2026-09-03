"""The review digest: every pair on one page, with what makes it doubtful.

``rdfeval review`` shows one pair in a terminal and asks for a verdict.  That
is the right shape for deciding and the wrong shape for deciding *fast*: the
reviewer cannot see what is coming, cannot jump to the pair a stratum's
conclusion rests on, and has to open the directory to reach the driver that
carries the proof.

This stage renders the same material as HTML — one page per stratum, plus an
index — with three things a terminal cannot give:

* **the proof next to the translation.**  The driver, its fixture and the
  context shim are what make a pair evidence rather than an assertion.  They
  are one click away instead of one directory away.
* **the risk flags.**  Everything a machine can notice about a pair that may
  be green without demonstrating anything — a driver with no call, a fixture
  with three triples, a ``demo()`` harness that is not identical on the two
  sides — is computed here and shown above the pair.  A flag decides
  nothing; it says where to look.
* **the verdicts, collected.**  A verdict is kept in the browser and
  rendered as an ``rdfeval review --set`` command to paste, so the page never
  writes to the study and a session survives a closed tab.

Nothing here changes a verdict, a metric or a status: the digest is a view,
regenerated from the pairs as they are.
"""

from __future__ import annotations

import ast
import csv
import html
from pathlib import Path

from .config import ROOT, RESULTS_SUMMARY
from .review import read_review
from .study import Study, STUDY
from .validate import iter_examples

REVIEW_DIR = ROOT / "results" / "review"

# A flag is (level, label, detail).  `danger` means the pair may be green
# without demonstrating anything; `warn` means a judgement was made that a
# reviewer should confirm; `info` is context, shown folded.
DANGER, WARN, INFO = "danger", "warn", "info"


# --------------------------------------------------------------- highlighting

def _highlighters():
    """Pygments lexers if they are installed, plain text otherwise.

    The digest must not become a reason for the pipeline to need a new
    dependency: without pygments every block still renders, uncoloured."""
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import PythonLexer, TextLexer
        from ldpy.pygments_lexer import LdpyLexer, TurtleLexer
    except ImportError:
        return None, {}, ""
    fmt = HtmlFormatter(nowrap=True)
    lexers = {"py": PythonLexer(), "ldpy": LdpyLexer(),
              "ttl": TurtleLexer(), "txt": TextLexer()}

    def render(text, kind):
        return highlight(text, lexers.get(kind, lexers["txt"]), fmt)

    # Two palettes: pygments' default is written for a white page and goes
    # nearly unreadable on the dark one the digest also renders.
    css = HtmlFormatter(style="default").get_style_defs(".hl")
    css += "\n@media (prefers-color-scheme: dark) {\n%s\n}\n" % (
        HtmlFormatter(style="github-dark").get_style_defs(".hl"))
    return render, lexers, css


_RENDER, _LEXERS, _PYGMENTS_CSS = _highlighters()


def _code(text: str, kind: str, numbered: bool = True) -> str:
    """One code block, line-numbered, escaped, coloured when possible."""
    body = _RENDER(text, kind) if _RENDER else html.escape(text)
    lines = body.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    if not numbered:
        return '<pre class="hl"><code>%s</code></pre>' % "\n".join(lines)
    rows = "\n".join(
        '<span class="ln">%4d</span>%s' % (i, ln)
        for i, ln in enumerate(lines, 1))
    return '<pre class="hl numbered"><code>%s</code></pre>' % rows


# ------------------------------------------------------------- what a pair is

def _files(ex_dir: Path) -> dict:
    """The pair's files, by role.

    Only five names are fixed.  Every other module is a **context shim** —
    the translator chooses its name, may need more than one, and may put it
    in a package directory when the region's own imports are relative.
    Fixtures are the same: one ``fixture.ttl`` is the common case, but a
    region with four branches may carry one Turtle file per branch."""
    known = {"original.py", "driver.py", "translated.ldpy", "meta.json",
             "review.json"}
    shims = sorted(q for q in ex_dir.rglob("*.py")
                   if q.name not in known and "__pycache__" not in q.parts)
    return {
        "original": ex_dir / "original.py",
        "translated": ex_dir / "translated.ldpy",
        "driver": ex_dir / "driver.py",
        "fixtures": sorted(ex_dir.rglob("*.ttl")),
        "shims": shims,
    }


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _driver_facts(path: Path) -> dict:
    """``run_pair``'s own arguments, read from the driver's syntax tree.

    Read rather than executed: the digest must be safe to regenerate over a
    corpus of three hundred drivers without running any of them."""
    facts = {"entry": None, "fixture": None, "calls": None, "parsed": False}
    try:
        tree = ast.parse(_read(path))
    except SyntaxError:
        return facts
    facts["parsed"] = True
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        name = getattr(node.func, "id", None) or getattr(
            node.func, "attr", None)
        if name != "run_pair":
            continue
        for kw in node.keywords:
            if kw.arg == "calls" and isinstance(kw.value, ast.List):
                facts["calls"] = len(kw.value.elts)
            elif kw.arg in ("entry", "fixture"):
                try:
                    facts[kw.arg] = ast.literal_eval(kw.value)
                except ValueError:
                    facts[kw.arg] = "<computed>"
    return facts


def _fixture_size(paths) -> int | None:
    """Triples over every Turtle fixture of the pair.

    ``None`` when the pair has none; ``-1`` when one of them is not Turtle."""
    paths = [q for q in paths if q.exists()]
    if not paths:
        return None
    total = 0
    for path in paths:
        try:
            from rdflib import Graph
            g = Graph()
            g.parse(data=_read(path), format="turtle")
            total += len(g)
        except Exception:                                # noqa: BLE001
            return -1
    return total


def _demo_bodies(files: dict) -> tuple[str | None, str | None]:
    """The ``demo()`` harness on each side, if there is one.

    A harness appended identically to both files is a legitimate device (a
    method extracted from a class needs a `self` that is not compared by
    identity).  What a reviewer must confirm is that it *is* identical: a
    harness that differs between the sides can hide the difference the pair
    is supposed to expose."""
    out = []
    for key in ("original", "translated"):
        text = _read(files[key])
        idx = text.find("\ndef demo(")
        out.append(text[idx:].strip() if idx >= 0 else None)
    return out[0], out[1]


# --------------------------------------------------------------------- flags

def _flags(ex_dir: Path, meta: dict, row: dict, files: dict) -> list:
    flags = []
    add = lambda lvl, label, detail: flags.append((lvl, label, detail))

    facts = _driver_facts(files["driver"])
    if not facts["parsed"]:
        add(DANGER, "driver unreadable",
            "driver.py does not parse — the pair cannot be read here")
    calls, kind = facts["calls"], meta.get("kind")
    if kind in ("function", "method") and not facts["entry"]:
        # The harness refuses a comparison with nothing observable in it, so
        # this is never a green over nothing.  What it can still be is a
        # green over the WRONG thing: module-state compares whatever the two
        # module levels leave behind, which need not depend on the region at
        # all.  Both hollow greens found by hand in this corpus had this
        # shape.
        add(WARN, "compared as module state",
            "the region is a function, but the driver names no entry point: "
            "what is compared is the module-level state — confirm it "
            "actually depends on what the translation changed")
    elif calls == 1 or (calls is None and facts["fixture"]):
        add(WARN, "one call only",
            "a single call exercises one path; the branches of the region "
            "are not compared")

    oracle = meta.get("oracle", "isomorphism")
    size = _fixture_size(files["fixtures"])
    if oracle == "values":
        if size is None:
            add(WARN, "reading region, no fixture file",
                "the oracle is the equality of the values produced; the "
                "input graph must then be built inside the pair — confirm "
                "it holds more than the region trivially finds")
        elif size == -1:
            add(DANGER, "fixture unparsable",
                "a .ttl file of the pair is not Turtle")
        elif size < 4:
            add(DANGER, "thin fixture",
                "%d triple(s): too little for several solutions, a zero-"
                "solution case and neighbourhood that must not match" % size)
        elif size < 8:
            add(WARN, "small fixture", "%d triples" % size)
    elif size is not None and size > 0:
        add(INFO, "fixture present",
            "%d triples, though the oracle is isomorphism" % size)

    orig_demo, tr_demo = _demo_bodies(files)
    if orig_demo or tr_demo:
        if orig_demo is None or tr_demo is None:
            add(DANGER, "demo() on one side only",
                "a harness on one side and not the other compares two "
                "different things")
        elif orig_demo != tr_demo:
            add(DANGER, "demo() harnesses differ",
                "the two harnesses are not textually identical — confirm the "
                "difference is not what the pair is meant to expose")
        else:
            add(WARN, "demo() harness on both sides",
                "scaffolding added identically to both files; it is excluded "
                "from neither surface measure, so confirm it is minimal")

    for shim in files["shims"]:
        n = len(_read(shim).splitlines())
        level = WARN if n > 80 else INFO
        add(level, "context shim: %s" % shim.relative_to(ex_dir),
            "%d lines of restored context — it must reproduce the origin "
            "repository, not invent logic" % n)

    cls = meta.get("classification")
    if cls and cls != "directly-expressible":
        add(WARN, "classified %s" % cls,
            "a judgement, not a measurement: it is what the aggregates count")
    if (meta.get("translation_status") == "final"
            and not meta.get("constructions")
            and cls not in ("not-expressible", "excluded")):
        add(WARN, "no construction declared",
            "a final pair that names no island is either trivial or "
            "unfilled")

    val = meta.get("validation") or {}
    if val.get("status") and val["status"] != "equivalent":
        add(DANGER, "validation: %s" % val["status"],
            val.get("error") or "; ".join(map(str, val.get("diffs", []))))

    if row:
        def num(key):
            try:
                return float(row.get(key) or 0)
            except ValueError:
                return 0.0
        if num("ratio_tokens") > 1.1 and cls not in (
                "not-expressible", "excluded"):
            add(WARN, "the translation grew",
                "%.0f%% more tokens than the rdflib version — the notation "
                "is supposed to remove scaffolding, not add it"
                % ((num("ratio_tokens") - 1) * 100))
        if num("ldpy_islands") == 0 and meta.get(
                "classification") == "directly-expressible":
            add(DANGER, "no island at all",
                "the translation uses no island, yet the pair is filed as "
                "directly expressible: there is nothing here to review")
        if num("ldpy_residual_constructors") > 0:
            add(INFO, "residual rdflib constructors",
                "%d constructor call(s) left in the translation"
                % num("ldpy_residual_constructors"))
    elif meta.get("translation_status") == "final":
        add(INFO, "not measured",
            "no row in pairs.csv — run `rdfeval compare`")

    order = {DANGER: 0, WARN: 1, INFO: 2}
    return sorted(flags, key=lambda f: order[f[0]])


# ---------------------------------------------------------------- rendering

def _github(meta: dict) -> str | None:
    repo, commit, path = (meta.get("repository"), meta.get("commit"),
                          meta.get("path"))
    if not (repo and commit and path):
        return None
    anchor = ""
    if meta.get("lineno"):
        anchor = "#L%s-L%s" % (meta["lineno"],
                               meta.get("end_lineno", meta["lineno"]))
    return "https://github.com/%s/blob/%s/%s%s" % (repo, commit, path, anchor)


_METRICS = [
    ("tokens", "python_tokens", "ldpy_tokens", "{:.0f}"),
    ("AST nodes", "python_syntax_nodes", "ldpy_syntax_nodes", "{:.0f}"),
    ("lines of code", "python_code_loc", "ldpy_code_loc", "{:.0f}"),
    ("scaffolding tokens / triple", "python_corr_scaffolding_tokens_per_triple",
     "ldpy_corr_scaffolding_tokens_per_triple", "{:.2f}"),
    ("nesting / term", "python_corr_nesting_per_term",
     "ldpy_corr_nesting_per_term", "{:.2f}"),
    ("constructors / triple", "python_corr_constructors_per_triple",
     "ldpy_corr_constructors_per_triple", "{:.2f}"),
]


def _metrics_table(row: dict) -> str:
    if not row:
        return ""
    cells = []
    for label, left, right, fmt in _METRICS:
        a, b = row.get(left, ""), row.get(right, "")
        if a == "" and b == "":
            continue
        def show(v):
            try:
                return fmt.format(float(v))
            except (TypeError, ValueError):
                return "—"
        better = ""
        try:
            if float(b or 0) < float(a or 0):
                better = " better"
        except ValueError:
            pass
        cells.append(
            "<tr><th>%s</th><td>%s</td><td class='ldpy%s'>%s</td></tr>"
            % (html.escape(label), show(a), better, show(b)))
    if not cells:
        return ""
    return ("<table class='metrics'><thead><tr><th></th><th>rdflib</th>"
            "<th>ldpy</th></tr></thead><tbody>%s</tbody></table>"
            % "".join(cells))


def _pair_html(ex_dir: Path, meta: dict, row: dict) -> str:
    files = _files(ex_dir)
    review = read_review(ex_dir)
    rid = meta["region_id"]
    flags = _flags(ex_dir, meta, row, files)
    worst = flags[0][0] if flags else "clean"
    status = review.get("review_status", "unreviewed")

    src = _github(meta)
    where = "%s@%s · %s · %s (L%s–L%s)" % (
        meta.get("repository", "?"), (meta.get("commit") or "")[:10],
        meta.get("path", "?"), meta.get("qualname", "?"),
        meta.get("lineno", "?"), meta.get("end_lineno", "?"))

    chips = [("stratum", meta.get("stratum")),
             ("oracle", meta.get("oracle", "isomorphism")),
             ("class", meta.get("classification") or "—"),
             ("status", meta.get("translation_status"))]
    chips_html = "".join(
        "<span class='chip'><b>%s</b> %s</span>" % (k, html.escape(str(v)))
        for k, v in chips)

    flags_html = "".join(
        "<li class='%s'><b>%s</b> — %s</li>"
        % (lvl, html.escape(label), html.escape(detail))
        for lvl, label, detail in flags) or "<li class='clean'>no flag</li>"

    notes = meta.get("translation_notes") or []
    notes_html = ""
    if notes:
        notes_html = (
            "<details><summary>translator's notes (%d)</summary><ol>%s</ol>"
            "</details>" % (len(notes), "".join(
                "<li>%s</li>" % html.escape(n) for n in notes)))

    extras = []
    driver = _read(files["driver"])
    if driver:
        facts = _driver_facts(files["driver"])
        extras.append(
            "<details><summary>driver.py — the proof "
            "(entry <code>%s</code>, %s call(s)%s)</summary>%s</details>"
            % (html.escape(str(facts["entry"] or "module")),
               facts["calls"] if facts["calls"] is not None else "no",
               ", fixture " + html.escape(str(facts["fixture"]))
               if facts["fixture"] else "",
               _code(driver, "py")))
    for fixture in files["fixtures"]:
        size = _fixture_size([fixture])
        extras.append(
            "<details><summary>%s — an input graph (%s)</summary>"
            "%s</details>"
            % (html.escape(fixture.name),
               "unparsable" if size == -1 else "%d triples" % size,
               _code(_read(fixture), "ttl")))
    for shim in files["shims"]:
        extras.append(
            "<details><summary>%s — restored context (%d lines)</summary>%s"
            "</details>" % (html.escape(str(shim.relative_to(ex_dir))),
                            len(_read(shim).splitlines()),
                            _code(_read(shim), "py")))

    return """
<section class="pair" id="{rid}" data-region="{rid}" data-risk="{worst}"
         data-status="{status}" data-final="{final}" tabindex="-1">
  <header>
    <h3><span class="marker"></span>{short}</h3>
    <div class="where">{where}{link}</div>
    <div class="chips">{chips}</div>
  </header>
  <ul class="flags">{flags}</ul>
  <div class="cols">
    <div class="col"><h4>original.py <span>rdflib</span></h4>{left}</div>
    <div class="col"><h4>translated.ldpy <span>ldpy</span></h4>{right}</div>
  </div>
  {metrics}
  {notes}
  {extras}
  <div class="verdict" data-region="{rid}">
    <button data-v="approved">approve</button>
    <button data-v="needs-work">needs work</button>
    <button data-v="rejected">reject</button>
    <input type="text" placeholder="comment (optional)" data-comment>
    <span class="recorded"></span>
  </div>
</section>""".format(
        rid=html.escape(rid), worst=worst, status=html.escape(status),
        final="yes" if meta.get("translation_status") == "final" else "no",
        short=html.escape(meta.get("qualname") or rid),
        where=html.escape(where),
        link=(" · <a href='%s' target='_blank'>source</a>" % html.escape(src)
              if src else ""),
        chips=chips_html, flags=flags_html,
        left=_code(_read(files["original"]), "py"),
        right=_code(_read(files["translated"]), "ldpy"),
        metrics=_metrics_table(row), notes=notes_html,
        extras="".join(extras))


# ------------------------------------------------------------ page furniture

_CSS = """
:root { --bg:#fff; --fg:#1a1a1a; --dim:#666; --line:#e3e3e3; --card:#fafafa;
        --danger:#b3261e; --warn:#8a6100; --info:#3a5a8a; --ok:#1e7a3c; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#16181c; --fg:#e6e6e6; --dim:#9aa0a6; --line:#2c2f36;
          --card:#1c1f24; --danger:#f2857c; --warn:#e0b25a; --info:#8fb4e8;
          --ok:#6fce90; } }
* { box-sizing:border-box }
body { margin:0; background:var(--bg); color:var(--fg);
       font:14px/1.5 -apple-system,Segoe UI,Roboto,sans-serif; }
a { color:var(--info) }
.top { position:sticky; top:0; z-index:5; background:var(--bg);
       border-bottom:1px solid var(--line); padding:.6rem 1rem;
       display:flex; gap:1rem; align-items:center; flex-wrap:wrap }
.top h1 { font-size:1rem; margin:0; font-weight:600 }
.top .count { color:var(--dim) }
.filters button, .verdict button { font:inherit; cursor:pointer;
       border:1px solid var(--line); background:var(--card); color:var(--fg);
       border-radius:6px; padding:.25rem .6rem }
.filters button.on { background:var(--fg); color:var(--bg) }
main { padding:1rem; max-width:2000px; margin:0 auto }
.pair { border:1px solid var(--line); border-radius:10px; margin:0 0 1.4rem;
        padding:.8rem 1rem; background:var(--card); scroll-margin-top:4rem }
.pair:focus { outline:2px solid var(--info) }
.pair h3 { margin:0; font-size:1rem; display:flex; gap:.5rem;
           align-items:center }
.marker { width:.6rem; height:.6rem; border-radius:50%; background:var(--dim);
          flex:0 0 auto }
[data-risk=danger] .marker { background:var(--danger) }
[data-risk=warn] .marker { background:var(--warn) }
[data-risk=info] .marker, [data-risk=clean] .marker { background:var(--ok) }
[data-status=approved] { border-color:var(--ok) }
[data-status=rejected] { border-color:var(--danger) }
.where { color:var(--dim); font-size:.82rem; margin:.2rem 0 }
.chips { display:flex; gap:.4rem; flex-wrap:wrap; margin:.4rem 0 }
.chip { border:1px solid var(--line); border-radius:99px;
        padding:.05rem .5rem; font-size:.75rem; color:var(--dim) }
.chip b { color:var(--fg); font-weight:600 }
.flags { list-style:none; margin:.5rem 0; padding:0; font-size:.82rem }
.flags li { padding:.15rem 0 .15rem .8rem; border-left:3px solid var(--line) }
.flags li.danger { border-color:var(--danger) } .flags b { font-weight:600 }
.flags li.warn { border-color:var(--warn) }
.flags li.info { border-color:var(--info); color:var(--dim) }
.flags li.clean { border-color:var(--ok); color:var(--dim) }
.cols { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:.8rem;
        margin-top:.6rem }
@media (max-width:1100px) { .cols { grid-template-columns:minmax(0,1fr) } }
.col h4 { margin:0 0 .3rem; font-size:.8rem; font-weight:600 }
.col h4 span { color:var(--dim); font-weight:400 }
pre.hl { margin:0; overflow-x:auto; background:var(--bg); border-radius:6px;
         border:1px solid var(--line); padding:.5rem .6rem;
         font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,monospace }
pre.hl .ln { color:var(--dim); user-select:none; padding-right:.8rem }
details { margin-top:.5rem; font-size:.85rem }
summary { cursor:pointer; color:var(--dim) }
details ol { font-size:.85rem }
table.metrics { border-collapse:collapse; margin-top:.6rem; font-size:.8rem }
table.metrics th, table.metrics td { border:1px solid var(--line);
        padding:.15rem .5rem; text-align:right }
table.metrics th { text-align:left; font-weight:500; color:var(--dim) }
table.metrics td.better { color:var(--ok); font-weight:600 }
.verdict { margin-top:.7rem; display:flex; gap:.5rem; align-items:center;
           flex-wrap:wrap }
.verdict input { flex:1; min-width:12rem; font:inherit; padding:.25rem .5rem;
        border:1px solid var(--line); border-radius:6px;
        background:var(--bg); color:var(--fg) }
.recorded { color:var(--ok); font-size:.8rem }
#tray { position:fixed; right:1rem; bottom:1rem; z-index:9; max-width:44rem }
#tray textarea { width:100%; height:9rem; font:12px/1.4 ui-monospace,monospace;
        border:1px solid var(--line); border-radius:8px; padding:.5rem;
        background:var(--card); color:var(--fg) }
#tray .bar { display:flex; gap:.5rem; justify-content:flex-end;
             margin-bottom:.3rem }
#tray button { font:inherit; cursor:pointer; border:1px solid var(--line);
        background:var(--card); color:var(--fg); border-radius:6px;
        padding:.25rem .6rem }
.hidden { display:none !important }
table.index { border-collapse:collapse; width:100% }
table.index th, table.index td { border-bottom:1px solid var(--line);
        padding:.35rem .6rem; text-align:right }
table.index th:first-child, table.index td:first-child { text-align:left }
"""

_JS = r"""
const KEY = 'rdfeval-review-verdicts';
const load = () => { try { return JSON.parse(localStorage.getItem(KEY)) || {}; }
                     catch (e) { return {}; } };
const save = v => { try { localStorage.setItem(KEY, JSON.stringify(v)); }
                    catch (e) {} };
let verdicts = load();

function commands() {
  return Object.entries(verdicts).map(([rid, v]) =>
    `rdfeval review --set ${v.verdict} --region ${rid}` +
    (v.comment ? ` -m ${JSON.stringify(v.comment)}` : '')).join('\n');
}

function paint() {
  document.querySelectorAll('.pair').forEach(p => {
    const v = verdicts[p.dataset.region];
    const box = p.querySelector('.recorded');
    if (v) { p.dataset.status = v.verdict; box.textContent = '→ ' + v.verdict; }
    else if (box) { box.textContent = ''; }
    p.querySelectorAll('.verdict button').forEach(b =>
      b.classList.toggle('on', !!v && b.dataset.v === v.verdict));
  });
  const t = document.querySelector('#tray textarea');
  if (t) t.value = commands();
  const n = document.getElementById('pending');
  if (n) n.textContent = Object.keys(verdicts).length;
  applyFilter();
}

function record(rid, verdict, comment) {
  if (verdicts[rid] && verdicts[rid].verdict === verdict && !comment) {
    delete verdicts[rid];
  } else {
    verdicts[rid] = {verdict, comment: comment || ''};
  }
  save(verdicts); paint();
}

let filter = 'todo';
function applyFilter() {
  document.querySelectorAll('.pair').forEach(p => {
    const decided = p.dataset.status === 'approved'
                 || p.dataset.status === 'rejected';
    const show = filter === 'all'
      || (filter === 'todo' && !decided && p.dataset.final === 'yes')
      || (filter === 'risk' && p.dataset.risk === 'danger')
      || (filter === 'done' && decided);
    p.classList.toggle('hidden', !show);
  });
  const shown = document.querySelectorAll('.pair:not(.hidden)').length;
  const c = document.getElementById('shown');
  if (c) c.textContent = shown;
}

document.addEventListener('click', e => {
  const b = e.target.closest('.verdict button');
  if (b) {
    const box = b.closest('.verdict');
    record(box.dataset.region, b.dataset.v,
           box.querySelector('[data-comment]').value.trim());
    return;
  }
  const f = e.target.closest('.filters button');
  if (f) {
    filter = f.dataset.f;
    document.querySelectorAll('.filters button').forEach(
      x => x.classList.toggle('on', x === f));
    applyFilter();
  }
});

document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  const shown = [...document.querySelectorAll('.pair:not(.hidden)')];
  if (!shown.length) return;
  const cur = document.activeElement.closest ?
    document.activeElement.closest('.pair') : null;
  let i = shown.indexOf(cur);
  if (e.key === 'j' || e.key === 'k') {
    i = e.key === 'j' ? Math.min(i + 1, shown.length - 1)
                      : Math.max(i - 1, 0);
    if (i < 0) i = 0;
    shown[i].focus(); shown[i].scrollIntoView({block: 'start'});
    e.preventDefault();
  } else if ('arw'.includes(e.key) && cur) {
    record(cur.dataset.region,
           {a: 'approved', r: 'rejected', w: 'needs-work'}[e.key],
           cur.querySelector('[data-comment]').value.trim());
    e.preventDefault();
  }
});

window.addEventListener('DOMContentLoaded', () => {
  const copy = document.getElementById('copy');
  if (copy) copy.onclick = () => navigator.clipboard.writeText(commands());
  const clear = document.getElementById('clear');
  if (clear) clear.onclick = () => {
    if (confirm('Forget every verdict recorded in this browser?')) {
      verdicts = {}; save(verdicts); paint();
    }
  };
  const toggle = document.getElementById('toggle-tray');
  if (toggle) toggle.onclick = () =>
    document.querySelector('#tray textarea').classList.toggle('hidden');
  paint();
});
"""


def _page(title: str, head: str, body: str, tray: bool = True) -> str:
    tray_html = ""
    if tray:
        tray_html = """
<div id="tray">
  <div class="bar">
    <button id="toggle-tray">commands</button>
    <button id="copy">copy</button>
    <button id="clear">forget all</button>
  </div>
  <textarea readonly class="hidden"></textarea>
</div>"""
    return """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%s</title><style>%s
%s</style></head>
<body>%s<main>%s</main>%s<script>%s</script></body></html>
""" % (html.escape(title), _CSS, _PYGMENTS_CSS, head, body, tray_html, _JS)


# ------------------------------------------------------------------- the run

def run(config: dict, study: Study = STUDY, stratum: str | None = None,
        out_dir: Path | None = None) -> None:
    out = out_dir or REVIEW_DIR
    rows = {}
    csv_path = study.path(RESULTS_SUMMARY / "pairs.csv")
    if csv_path.exists():
        with csv_path.open(encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                rows[row["region_id"]] = row

    by_stratum: dict[str, list] = {}
    for ex_dir, meta in iter_examples(study):
        by_stratum.setdefault(meta.get(study.group, "?"), []).append(
            (ex_dir, meta))

    out.mkdir(parents=True, exist_ok=True)
    index_rows, totals = [], {"final": 0, "draft": 0, "danger": 0,
                              "approved": 0, "rejected": 0}
    for name in sorted(by_stratum):
        if stratum and name != stratum:
            continue
        pairs = by_stratum[name]
        sections, counts = [], {"final": 0, "draft": 0, "danger": 0,
                                "approved": 0, "rejected": 0}
        for ex_dir, meta in pairs:
            row = rows.get(meta["region_id"], {})
            fragment = _pair_html(ex_dir, meta, row)
            sections.append(fragment)
            final = meta.get("translation_status") == "final"
            counts["final" if final else "draft"] += 1
            # Only a final pair can be flagged in a way that means anything:
            # a draft has no driver yet, so every screen fires on it.
            if final and 'data-risk="danger"' in fragment:
                counts["danger"] += 1
            st = read_review(ex_dir).get("review_status")
            if st in counts:
                counts[st] += 1
        head = """
<div class="top">
  <h1><a href="index.html">digest</a> · %s</h1>
  <span class="count">%d final, %d draft · <span id="shown">0</span> shown ·
    <span id="pending">0</span> verdict(s) held</span>
  <span class="filters">
    <button data-f="todo" class="on">to review</button>
    <button data-f="risk">flagged</button>
    <button data-f="done">decided</button>
    <button data-f="all">all</button>
  </span>
  <span class="count">j/k move · a/r/w decide</span>
</div>""" % (html.escape(name), counts["final"], counts["draft"])
        (out / ("%s.html" % name)).write_text(
            _page("digest · %s" % name, head, "".join(sections)),
            encoding="utf-8")
        index_rows.append((name, counts))
        for k in totals:
            totals[k] += counts[k]

    if stratum:
        # One stratum was asked for: the index would then claim the study is
        # that stratum, which is worse than no index at all.
        print("digest: %s -> %s (index left as it was)"
              % (stratum, out / ("%s.html" % stratum)))
        return

    body = ["<table class='index'><thead><tr><th>stratum</th><th>final</th>"
            "<th>draft</th><th>flagged</th><th>approved</th><th>rejected</th>"
            "</tr></thead><tbody>"]
    for name, c in index_rows:
        body.append(
            "<tr><td><a href='%s.html'>%s</a></td><td>%d</td><td>%d</td>"
            "<td>%d</td><td>%d</td><td>%d</td></tr>"
            % (html.escape(name), html.escape(name), c["final"], c["draft"],
               c["danger"], c["approved"], c["rejected"]))
    body.append("<tr><th>total</th><th>%d</th><th>%d</th><th>%d</th>"
                "<th>%d</th><th>%d</th></tr>"
                % (totals["final"], totals["draft"], totals["danger"],
                   totals["approved"], totals["rejected"]))
    body.append("</tbody></table>")
    body.append(
        "<p style='color:var(--dim);max-width:46rem;margin-top:1.5rem'>"
        "A flag says where to look, never what to decide. Verdicts are held "
        "in this browser and shown as <code>rdfeval review --set</code> "
        "commands to paste; nothing on these pages writes to the study.</p>")

    (out / "index.html").write_text(
        _page("review digest", "<div class='top'><h1>review digest</h1>"
              "<span class='count'>%d final · %d draft · %d flagged</span>"
              "</div>" % (totals["final"], totals["draft"], totals["danger"]),
              "".join(body), tray=False),
        encoding="utf-8")
    print("digest: %d strata, %d final, %d draft, %d flagged -> %s"
          % (len(index_rows), totals["final"], totals["draft"],
             totals["danger"], out / "index.html"))

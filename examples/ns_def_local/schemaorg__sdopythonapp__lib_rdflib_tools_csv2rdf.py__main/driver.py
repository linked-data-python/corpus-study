"""Validation driver for schemaorg__sdopythonapp__lib_rdflib_tools_csv2rdf.py__main.

`main()` is a command line: it takes no argument, it reads sys.argv, builds a
CSV2RDF converter, sets its BASE and PROPBASE to `rdflib.Namespace(...)` (six
sites: the -f configuration file, -b/-p, --base/--propbase) and its CLASS and
PROPS to `rdflib.URIRef(...)` (five more), then runs the conversion.  The
Namespaces are never dereferenced in main(): they are STORED, and what they
are worth shows when `convert` mints the instance IRIs (BASE) and the property
IRIs (PROPBASE) it writes to stdout or to the `-o` file.  So each call sets
sys.argv and the harness compares what the conversion printed (stdout,
stderr -- the elapsed time is filtered) and the files it wrote.

Calls (data.csv has two rows, and a header whose labels become properties):

  * -o with -b / -p / -c / -l: the converted triples land in a file of this
    directory (the harness compares its content as a graph and deletes it);
  * --out with --base / -p / --class / --defineclass;
  * -b, -p given AND --base (the long form is read after, wins);
  * --propbase: the original ALWAYS raises ValueError on it -- the closing
    loop reads `--propbase` as `--prop<N>` and calls int("base") -- so that
    site of the Namespace is visible only as that raise (a translation that
    fails to run it, or to raise afterwards, differs);
  * -f configuration file only (its `base`, `propbase`, `class`, `prop1`...);
  * -f together with -b/-p (the command line overrides the file);
  * -f with another delimiter, a skipped line and a relative class IRI
    (`Thing`, which must stay relative) with defineclass;
  * -o only: no base, no propbase, convert falls back on its own;
  * no -o: stdout is the harness's StringIO, which has no `.name`, so
    convert() raises AttributeError before it uses any Namespace -- a raise,
    compared like a value;
  * -h: help is printed, then sys.exit(-1) (turned into an exception below,
    because the harness catches Exception, not SystemExit);
  * -s not an integer: ValueError.

Neither `-i` nor `ident=` is used: the installed rdflib's CSV2RDF still has
a Python 2 line there (`x.encode("utf8").replace(" ", "_")`), TypeError on
the first row, with or without the translation.

`config.readfp(...)` of the original does not exist in Python 3.12: both
sides call `config.read_file(...)` (Graph.load precedent, no RDF meaning).
"""
import fileinput
import os
import re
import sys
from pathlib import Path

from rdfeval import harness
from rdfeval.harness import run_pair

HERE = Path(__file__).resolve().parent
CSV = str(HERE / "data.csv")
CSV2 = str(HERE / "data_semicolon.csv")
CONF = str(HERE / "conf_ns.ini")
CONF2 = str(HERE / "conf_semicolon.ini")
OUT = str(HERE / "converted.n3")
OUT2 = str(HERE / "converted-long.n3")

_exec_artefact = harness._exec_artefact


def _sys_exit_as_exception(path, name):
    ns, out = _exec_artefact(path, name)
    main = ns.get("main")
    if callable(main):
        def call():
            try:
                return main()
            except SystemExit as e:
                raise RuntimeError(f"SystemExit({e.code})")
        call.__qualname__ = main.__qualname__
        ns["main"] = call
    return ns, out


harness._exec_artefact = _sys_exit_as_exception


def _argv(*args):
    def build():
        fileinput.close()               # a previous failed call may have left it open
        os.chdir(HERE)                  # the configuration files name their output relatively
        sys.argv = ["csv2rdf", *args]
        return (), {}
    return build


def _no_time(text):
    return re.sub(r"Took [0-9.]+ seconds\.", "Took N seconds.", text)


VERDICT = run_pair(
    __file__,
    entry="main",
    stdout_filter=_no_time,
    calls=[
        _argv("-o", OUT, "-b", "http://short.example.org/inst/", "-p", "http://short.example.org/prop#",
              "-c", "http://short.example.org/Thing", "-l", "(1,)", CSV),
        _argv("--out", OUT2, "--base", "http://long.example.org/inst/", "-p", "http://long.example.org/prop/",
              "--class", "http://long.example.org/Thing", "--defineclass", CSV),
        _argv("-o", OUT, "-b", "http://ignored.example.org/", "-p", "http://kept.example.org/p/",
              "--base", "http://wins.example.org/", CSV),
        _argv("-o", OUT, "-b", "http://before-the-raise.example.org/", "--propbase", "http://long.example.org/prop/", CSV),
        _argv("-f", CONF, CSV),
        _argv("-f", CONF, "-b", "http://cli.example.org/inst/", "-p", "http://cli.example.org/prop/", CSV),
        _argv("-f", CONF2, CSV2),
        _argv("-o", OUT, CSV),
        _argv(CSV),
        _argv("-h"),
        _argv("-s", "many", CSV),
    ],
)

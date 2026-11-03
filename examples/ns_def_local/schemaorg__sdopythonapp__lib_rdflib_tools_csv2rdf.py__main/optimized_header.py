# Extracted from schemaorg/sdopythonapp@128be97d35 : lib/rdflib/tools/csv2rdf.py
# region: main (lines 443-541, stratum ns_def_local)
# licence of the source repository: see meta.json
import sys
import getopt
import fileinput
import codecs
import rdflib
from six.moves import configparser
from csv2rdf_context import CSV2RDF, column, csv_reader
HELP = """
csv2rdf.py \
    -b <instance-base> \
    -p <property-base> \
    [-D <default>] \
    [-c <classname>] \
    [-i <identity column(s)>] \
    [-l <label columns>] \
    [-s <N>] [-o <output>] \
    [-f configfile] \
    [--col<N> <colspec>] \
    [--prop<N> <property>] \
    <[-d <delim>] \
    [-C] [files...]"

Reads csv files from stdin or given files
if -d is given, use this delimiter
if -s is given, skips N lines at the start
Creates a URI from the columns given to -i, or automatically by numbering if
none is given
Outputs RDFS labels from the columns given to -l
if -c is given adds a type triple with the given classname
if -C is given, the class is defined as rdfs:Class
Outputs one RDF triple per column in each row.
Output is in n3 format.
Output is stdout, unless -o is specified

Long options also supported: \
    --base, \
    --propbase, \
    --ident, \
    --class, \
    --label, \
    --out, \
    --defineclass

Long options --col0, --col1, ...
can be used to specify conversion for columns.
Conversions can be:
    ignore, float(), int(), split(sep, [more]), uri(base, [class]), date(format)

Long options --prop0, --prop1, ...
can be used to use specific properties, rather than ones auto-generated
from the headers

-D sets the default conversion for columns not listed

-f says to read config from a .ini/config file - the file must contain one
section called csv2rdf, with keys like the long options, i.e.:

[csv2rdf]
out=output.n3
base=http://example.org/
col0=split(";")
col1=split(";", uri("http://example.org/things/",
                    "http://xmlns.com/foaf/0.1/Person"))
col2=float()
col3=int()
col4=date("%Y-%b-%d %H:%M:%S")

"""

def main():
    csv2rdf = CSV2RDF()

    opts, files = getopt.getopt(
        sys.argv[1:],
        "hc:b:p:i:o:Cf:l:s:d:D:",
        ["out=", "base=", "delim=", "propbase=", "class=", "default="
         "ident=", "label=", "skip=", "defineclass", "help"])
    opts = dict(opts)

    if "-h" in opts or "--help" in opts:
        print(HELP)
        sys.exit(-1)

    converters = {
        "out": ("-o", lambda v: codecs.open(v, "w", "utf-8")),
        "base": ("-b", rdflib.Namespace),
        "delim": ("-d", str),
        "default": ("-D", column),
        "propbase": ("-p", rdflib.Namespace),
        "label": ("-l", eval),
        "ident": ("-i", eval),
        "skip": ("-s", int),
        "class": ("-c", rdflib.URIRef),
    }

    if "-f" in opts:
        config = configparser.ConfigParser()
        config.read_file(open(opts["-f"]))
        for k, v in config.items("csv2rdf"):
            if k in converters:
                setattr(csv2rdf, k.upper(), converters[k][1](v))
            elif k == "defineclass":
                csv2rdf.DEFINECLASS = bool(v)
            elif k.startswith("col"):
                csv2rdf.COLUMNS[int(k[3:])] = column(v)
            elif k.startswith("prop"):
                csv2rdf.PROPS[int(k[4:])] = rdflib.URIRef(v)

    for name, (short, convert) in converters.items():
        for option in (short, "--" + name):
            if option in opts:
                setattr(csv2rdf, name.upper(), convert(opts[option]))

    for k, v in opts.items():
        if k.startswith("--col"):
            csv2rdf.COLUMNS[int(k[5:])] = column(v)
        elif k.startswith("--prop"):
            csv2rdf.PROPS[int(k[6:])] = rdflib.URIRef(v)

    if csv2rdf.CLASS and ("-C" in opts or "--defineclass" in opts):
        csv2rdf.DEFINECLASS = True

    csv2rdf.convert(
        csv_reader(fileinput.input(files), delimiter=csv2rdf.DELIM))

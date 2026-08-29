# Context shim (see meta.json): CSV2RDF, toProperty, index, prefixuri,
# csv_reader and the module-level `uris` dict, transcribed VERBATIM from
# globalPlugins/contextLabeler/_vendor/rdflib/tools/csv2rdf.py of
# shubhamjakhete/nvda_reader@8b5fb51e42 (local clone: corpus/repos/
# shubhamjakhete__nvda_reader/.../csv2rdf.py, lines 96-138, 301-438). Itself
# a vendored copy of rdflib.tools.csv2rdf, unmodified here.
#
# Left out (not transcribed): the NodeMaker / NodeUri / NodeFloat / NodeInt /
# NodeBool / NodeReplace / NodeDate / NodeSplit family, `default_node_make`,
# `column()` and `config_functions` -- reachable only via -f / -D / --default
# / --col* on the command line, none of which this region's fixture passes
# (see driver.py: -b, -p, -o, one CSV file). Python resolves a name only
# when the line using it actually executes, so the CSV2RDF class below is
# otherwise left complete and byte-for-byte as in the source -- these
# branches are simply never taken, exactly as `main()` leaves them untaken
# when a user does not pass those options.
import sys
import time
import warnings
from typing import Any, Dict, Optional, Tuple, List
from urllib.parse import quote

import rdflib
from rdflib.namespace import RDF, RDFS, split_uri
from rdflib.term import URIRef

# bah - ugly global
uris: Dict[Any, Tuple[URIRef, Optional[URIRef]]] = {}


def toProperty(label):
    """
    CamelCase + lowercase initial a string


    FIRST_NM => firstNm

    firstNm => firstNm

    """
    import re

    label = re.sub(r"[^\w]", " ", label)
    label = re.sub("([a-z])([A-Z])", "\\1 \\2", label)
    label = label.split(" ")
    return "".join([label[0].lower()] + [x.capitalize() for x in label[1:]])


def toPropertyLabel(label):
    if not label[1:2].isupper():
        return label[0:1].lower() + label[1:]
    return label


def index(l_: List[int], i: Tuple[int, ...]) -> Tuple[int, ...]:
    """return a set of indexes from a list
    >>> index([1,2,3],(0,2))
    (1, 3)
    """
    return tuple([l_[x] for x in i])


def csv_reader(csv_data, dialect=None, **kwargs):
    import csv

    dialect = dialect or csv.excel
    csv_reader = csv.reader(csv_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield row


def prefixuri(x, prefix, class_: Optional[URIRef] = None):
    if prefix:
        r = rdflib.URIRef(prefix + quote(x.encode("utf8").replace(" ", "_"), safe=""))
    else:
        r = rdflib.URIRef(x)
    uris[x] = (r, class_)
    return r


class CSV2RDF:
    def __init__(self):
        self.CLASS = None
        self.BASE = None
        self.PROPBASE = None
        self.IDENT = "auto"
        self.LABEL = None
        self.DEFINECLASS = False
        self.SKIP = 0
        self.DELIM = ","
        self.DEFAULT = None

        self.COLUMNS = {}
        self.PROPS = {}

        self.OUT = sys.stdout

        self.triples = 0

    def triple(self, s, p, o):
        self.OUT.write("%s %s %s .\n" % (s.n3(), p.n3(), o.n3()))
        self.triples += 1

    def convert(self, csvreader):
        start = time.time()

        if self.OUT:
            sys.stderr.write("Output to %s\n" % self.OUT.name)

        if self.IDENT != "auto" and not isinstance(self.IDENT, tuple):
            self.IDENT = (self.IDENT,)

        if not self.BASE:
            warnings.warn("No base given, using http://example.org/instances/")
            self.BASE = rdflib.Namespace("http://example.org/instances/")

        if not self.PROPBASE:
            warnings.warn("No property base given, using http://example.org/props/")
            self.PROPBASE = rdflib.Namespace("http://example.org/props/")

        # skip lines at the start
        for x in range(self.SKIP):
            next(csvreader)

        # read header line
        header_labels = list(next(csvreader))
        headers = dict(enumerate([self.PROPBASE[toProperty(x)] for x in header_labels]))
        # override header properties if some are given
        for k, v in self.PROPS.items():
            headers[k] = v
            header_labels[k] = split_uri(v)[1]

        if self.DEFINECLASS:
            # output class/property definitions
            self.triple(self.CLASS, RDF.type, RDFS.Class)
            for i in range(len(headers)):
                h, l_ = headers[i], header_labels[i]
                if h == "" or l_ == "":
                    continue
                if self.COLUMNS.get(i, self.DEFAULT) == "ignore":
                    continue
                self.triple(h, RDF.type, RDF.Property)
                self.triple(h, RDFS.label, rdflib.Literal(toPropertyLabel(l_)))
                self.triple(h, RDFS.domain, self.CLASS)
                self.triple(
                    h, RDFS.range, self.COLUMNS.get(i, default_node_make).range()
                )

        rows = 0
        for l_ in csvreader:
            try:
                if self.IDENT == "auto":
                    uri = self.BASE["%d" % rows]
                else:
                    uri = self.BASE[
                        "_".join(
                            [
                                quote(x.encode("utf8").replace(" ", "_"), safe="")
                                for x in index(l_, self.IDENT)
                            ]
                        )
                    ]

                if self.LABEL:
                    self.triple(
                        uri, RDFS.label, rdflib.Literal(" ".join(index(l_, self.LABEL)))
                    )

                if self.CLASS:
                    # type triple
                    self.triple(uri, RDF.type, self.CLASS)

                for i, x in enumerate(l_):
                    x = x.strip()
                    if x != "":
                        if self.COLUMNS.get(i, self.DEFAULT) == "ignore":
                            continue
                        try:
                            o = self.COLUMNS.get(i, rdflib.Literal)(x)
                            if isinstance(o, list):
                                for _o in o:
                                    self.triple(uri, headers[i], _o)
                            else:
                                self.triple(uri, headers[i], o)

                        except Exception as e:
                            warnings.warn(
                                "Could not process value for column "
                                + "%d:%s in row %d, ignoring: %s "
                                % (i, headers[i], rows, e.message)
                            )

                rows += 1
                if rows % 100000 == 0:
                    sys.stderr.write(
                        "%d rows, %d triples, elapsed %.2fs.\n"
                        % (rows, self.triples, time.time() - start)
                    )
            except Exception:
                sys.stderr.write("Error processing line: %d\n" % rows)
                raise

        # output types/labels for generated URIs
        classes = set()
        for l_, x in uris.items():
            u, c = x
            self.triple(u, RDFS.label, rdflib.Literal(l_))
            if c:
                c = rdflib.URIRef(c)
                classes.add(c)
                self.triple(u, RDF.type, c)

        for c in classes:
            self.triple(c, RDF.type, RDFS.Class)

        self.OUT.close()
        sys.stderr.write("Converted %d rows into %d triples.\n" % (rows, self.triples))
        sys.stderr.write("Took %.2f seconds.\n" % (time.time() - start))

"""Validation driver for tteon__seocho__src_seocho_ontology_serialization.py__ontology_to_ttl.

The region builds an rdflib Graph but never exposes it: it serialises it
straight to a file and returns the output ``Path``.  Comparing the two
returned ``Path`` objects (as ``rdfeval.harness.run_pair``'s automatic
entry-mode comparison would) proves nothing about the graph's content, so
this driver calls both versions itself, reads each Turtle file back into a
fresh graph, and checks isomorphism directly (the region's own oracle,
per meta.json: ``"oracle": "isomorphism"``).
"""
import io
import json
import sys
import tempfile
import traceback
from contextlib import redirect_stdout
from pathlib import Path

from rdfeval.harness import graphs_isomorphic
from shim import NodeDef, Ontology, Property, PropertyType, RelDef


def _make_ontology() -> Ontology:
    return Ontology(
        name="Company Graph",
        namespace="https://example.org/onto/",
        description="A small ontology of companies and people.",
        nodes={
            "Company": NodeDef(
                description="A registered business entity.",
                aliases=["Business", "Firm"],
                properties={
                    "name": Property(PropertyType.STRING, description="Legal name"),
                    "founded": Property(PropertyType.DATETIME),
                },
            ),
            "Startup": NodeDef(
                description="A young company.",
                broader=["Company"],
                same_as=None,
            ),
            "Person": NodeDef(
                same_as="http://schema.org/Person",
                properties={
                    "age": Property(PropertyType.INTEGER),
                },
            ),
        },
        relationships={
            "worksFor": RelDef(
                source="Person",
                target="Company",
                description="Employment relationship.",
                aliases=["employedBy"],
            ),
            "sameAs": RelDef(same_as="http://www.w3.org/2002/07/owl#sameAs"),
        },
    )


def _run(path: Path) -> tuple[object, str, str | None]:
    ns: dict = {"__name__": "__mod__", "__file__": str(path)}
    out = io.StringIO()
    try:
        if path.suffix == ".ldpy":
            from ldpy.transpiler import transpile
            r = transpile(path.read_text(), filename=str(path))
            code = compile(r.code, str(path), "exec")
        else:
            code = compile(path.read_text(), str(path), "exec")
        with redirect_stdout(out):
            exec(code, ns)
        return ns, out.getvalue(), None
    except Exception:
        return ns, out.getvalue(), traceback.format_exc(limit=8)


def main() -> None:
    ex_dir = Path(__file__).resolve().parent
    verdict: dict = {"example": ex_dir.name, "equivalent": False,
                     "method": "call:ontology_to_ttl+read-back-isomorphism",
                     "diffs": [], "error": None}

    ns_o, out_o, err_o = _run(ex_dir / "original.py")
    ns_t, out_t, err_t = _run(ex_dir / "translated.ldpy")
    if err_o or err_t:
        verdict["error"] = f"original: {err_o}\ntranslated: {err_t}"
        print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
        return

    diffs: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        out_path_o = tmp_path / "original.ttl"
        out_path_t = tmp_path / "translated.ttl"
        try:
            ns_o["ontology_to_ttl"](_make_ontology(), out_path_o)
            ns_t["ontology_to_ttl"](_make_ontology(), out_path_t)
        except Exception:
            verdict["error"] = traceback.format_exc(limit=8)
            print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)
            return

        from rdflib import Graph
        g_o = Graph().parse(source=str(out_path_o), format="turtle")
        g_t = Graph().parse(source=str(out_path_t), format="turtle")
        if not graphs_isomorphic(g_o, g_t):
            diffs.append(
                f"serialised graphs not isomorphic ({len(g_o)} vs {len(g_t)} triples)"
            )

    if out_o != out_t:
        diffs.append("stdout differs at module level")

    verdict["diffs"] = diffs
    verdict["equivalent"] = not diffs
    print("RDFEVAL-VERDICT " + json.dumps(verdict), file=sys.stderr)


if __name__ == "__main__":
    main()

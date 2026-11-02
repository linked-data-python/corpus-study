# Context shim (see meta.json), for judaicalink/judaicalink-labs@b683b52eaa,
# labs/data/management/commands/legacy/generate_rujen_translation.py.
#
# The region cannot run outside the Django package and without the network:
#   * `from ._dataset_command import DatasetCommand, jlo, skos, log, error`:
#     the real module imports django, scrapy and toml. Reproduced here: the
#     namespaces `jlo` and `skos` (same IRIs as `namespaces` in
#     labs/data/management/commands/_dataset_command.py), the two loggers
#     (the real module names both `logging.getLogger(__name__)`, i.e.
#     "labs.data.management.commands._dataset_command"), and an empty
#     `DatasetCommand` (imported by the module for its `Command` class, which
#     is outside the region and never used by it).
#   * `from googletrans import Translator`: a web client of Google Translate,
#     not installed and unusable offline. `Translator.translate(text, src,
#     dest)` is reduced to a deterministic table lookup returning an object
#     with the attributes the region reads (`text`, `src`, `dest`), whose
#     str() has the shape of googletrans.models.Translated.__str__ -- the
#     region puts that object, not `.text`, into `rdflib.Literal`.
#   * `configure_task(task)` is the source's own function of the same name,
#     which sets module globals (`prop`, `dest_lang`, ...); here it takes the
#     globals of the module it configures, since a function defined in this
#     shim would otherwise set the shim's own globals.
#
# Identical bindings for both representations.
import logging

from rdflib import Namespace

jlo = Namespace("http://data.judaicalink.org/ontology/")
skos = Namespace("http://www.w3.org/2004/02/skos/core#")

log = logging.getLogger("labs.data.management.commands._dataset_command")
error = logging.getLogger("labs.data.management.commands._dataset_command")


class DatasetCommand:
    pass


class Translated:
    def __init__(self, src, dest, origin, text):
        self.src = src
        self.dest = dest
        self.origin = origin
        self.text = text
        self.pronunciation = None
        self.extra_data = {}

    def __str__(self):
        return ("Translated(src={src}, dest={dest}, text={text}, "
                "pronunciation={pronunciation}, extra_data={extra_data})").format(
                    src=self.src, dest=self.dest, text=self.text,
                    pronunciation=self.pronunciation,
                    extra_data='"' + repr(self.extra_data)[:10] + '..."')


# What the stand-in "service" knows (Russian -> English / German); anything
# else comes back unchanged, i.e. still in Cyrillic.
KNOWN = {
    "Давид Бен-Гурион": {"en": "David Ben-Gurion", "de": "David Ben-Gurion"},
    "Еврейская энциклопедия": {"en": "Jewish encyclopedia", "de": "Juedische Enzyklopaedie"},
    "Историк": {"en": "Historian", "de": "Historiker"},
    "Писатель и журналист": {"en": "Writer and journalist", "de": "Schriftsteller und Journalist"},
}
# Texts for which the service answers as a banned client does (the source
# language comes back as something else than "ru"), whatever the instance.
BANNED = {"Раввин"}


class Translator:
    def translate(self, text, src="auto", dest="en"):
        text = str(text)
        if text in BANNED:
            return Translated(src="en", dest=dest, origin=text, text=text)
        found = KNOWN.get(text, {}).get(dest, text)
        return Translated(src=src, dest=dest, origin=text, text=found)


def configure_task(task, namespace):
    if task == "en-label":
        namespace["cachefile"] = "en_label_cache.csv"
        namespace["outfile"] = "rujen-en-label-translations.ttl"
        namespace["dest_lang"] = "en"
        namespace["prop"] = skos.prefLabel
    elif task == "en-abstract":
        namespace["cachefile"] = "en_abstract_cache.csv"
        namespace["outfile"] = "rujen-en-abstract-translations.ttl"
        namespace["dest_lang"] = "en"
        namespace["prop"] = jlo.hasAbstract
    elif task == "de-label":
        namespace["cachefile"] = "de_label_cache.csv"
        namespace["outfile"] = "rujen-de-label-translations.ttl"
        namespace["dest_lang"] = "de"
        namespace["prop"] = skos.prefLabel
    elif task == "de-abstract":
        namespace["cachefile"] = "de_abstract_cache.csv"
        namespace["outfile"] = "rujen-de-abstract-translations.ttl"
        namespace["dest_lang"] = "de"
        namespace["prop"] = jlo.hasAbstract

import re, json
from .tools import get
from .humans import numbers as transform_numbers
from .objects import *

class Alexa:
    _alexa_name_patern = re.compile('[^a-zA-Z0-9_]+')
    def _alexa_name(self, string):
        return transform_numbers(self._alexa_name_patern.sub('_', string).lower())

class AlexaGenerator(Alexa):
    def __init__(self):
        pass

    def generate(self, source, lang="en"):
        name, intents, entities = source.get_name(), source.get_intents(), source.get_entities()
        ret = {
            "interactionModel": {
                "languageModel": {
                    "invocationName": name,
                    "intents": self.generate_intents(intents, add_default=True, lang=lang),
                    "types": self.generate_entities(entities, lang=lang)
                }
            }
        }
        return json.dumps(ret, indent=2)

    def generate_intents(self, intents, add_default=True, lang="en"):
        """
        Read intents objects, and generate alexa intents
        """
        ret = []
        for intent in intents.values():
            samples = intent.samples.get(lang)
            if not samples:
                continue
            item = {
                "name": self._alexa_name(intent.get("name")),
                "samples": ["".join([self.get_sample_element(item) for item in items]) for items in samples]
            }
            slots = [{"name":name, "type": atype} for (name, atype) in self.collect_slots(samples)]
            if slots:
                item["slots"] = slots
            ret.append(item)
        return ret

    def _get_type(self, item):
        """
        Given an object Item, determine whether the type is Standard ot Custom
        Return : type name, True if LITERAL
        """
        meta = item.meta
        if meta and type(meta) == StandardType:
            meta = meta.get("alexa")
            return meta, meta == "AMAZON.LITERAL"
        elif meta and type(meta) == CustomType:
            meta = meta.name
            return self._alexa_name(meta), False
        raise Exception("item %r has not type" % item)

    def collect_slots(self, samples):
        """
        Read all samples and collect slots mentionned
        Return: list of (slot name, type)
        """
        slots = set()
        for sample in samples:
            for item in sample:
                alias = item.name
                if alias:
                    meta, _ = self._get_type(item)
                    slots.add((self._alexa_name(alias), meta))
        return slots

    _alexa_sample_pattern = re.compile('[^a-zA-Z0-9{} ]+')
    def get_sample_element(self, item):
        """
        Given an Item object, generate the Alexa representation of the part of sample is represents
        Return: string
        """
        alias, source_text = item.name, item.text
        text = transform_numbers(source_text)
        text = self._alexa_sample_pattern.sub('', text)
        if alias:
            _, example = self._get_type(item)
            if example:
                return " {%s|%s} " % (text, self._alexa_name(alias))
            return " {%s} " % self._alexa_name(alias)
        return text

    def generate_entities(self, entities, lang="en"):
        """
        """
        ret = []
        for entity in entities.values():
            ret.append({
                "name": self._alexa_name(entity.get("name")),
                "values": [{"name": entry} for entry in entity.get_entries(lang)]
            })
        return ret


class AlexaResponseGenerator(Alexa):
    def __init__(self):
        pass

    def generate(self, source, lang="en"):
        intents = source.get_intents()
        ret = {}
        for intent in intents.values():
            name = self._alexa_name(intent.get("name"))
            resp = intent.responses.get(lang)
            if resp:
                ret[name] = list(filter(lambda x:x is not None, resp))
        return json.dumps(ret, indent=2)

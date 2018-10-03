import re, sys, json
from .tools import get
from .humans import numbers as transform_numbers
from .objects import *

class Rasa:
    _name_patern = re.compile('[ \t]')
    def _rasa_name(self, string):
        return self._name_patern.sub('_', string).lower()

class RasaMarkDownGenerator(Rasa):
    def __init__(self):
        pass

    def generate(self, source, lang="en", **kwargs):
        _, intents, entities = source.get_name(), source.get_intents(), source.get_entities()
        outfile = []
        for _, intent in intents.items():
            outfile.extend(self.generate_intent(intent, lang=lang))
        for _, entity in entities.items():
            outfile.extend(self.generate_entity(entity, lang=lang))            
        return "\n".join(outfile)

    def generate_intent(self, intent, lang="en"):
        name = intent.get("name")
        samples = intent.samples.get(lang)
        if samples:
            ret = [ "## intent:%s" % self._rasa_name(name) ]
            for sample in samples:
                ret.append("- %s" % self.generate_sample(sample))
            return ret
        return []

    def generate_sample(self, sample):
        return "".join(map(self.generate_item, sample))

    def generate_item(self, item):
        if item.name:
            #atype = self.get_type(item)
            #if atype is None:
            return "[%s](%s)" % (item.text, item.name)    
            #return "[%s](%s:%s)" % (item.text, item.name, atype)
        return item.text

    def get_type(self, item):
        """
        Given an object Item, determine whether the type is Standard ot Custom
        Return : type name
        """
        meta = item.meta
        if meta and type(meta) == StandardType:
            meta = meta.get("rasanlu")
            if isinstance(meta, Type):
                return None
            return meta
        elif meta and type(meta) == CustomType:
            meta = meta.name
            return self._rasa_name(meta)

    def generate_entity(self, entity, lang="en"):
        name = entity.get("name")
        ret = [ "## synonym:%s" % self._rasa_name(name) ]
        entries = set()
        for entry in entity.entries.get(lang) or []:
            entries.add(entry.get("value"))
            entries |= set(entry.get("synonyms"))
        ret.extend(map(lambda x:"- %s"%x, entries))
        return ret



class RasaResponseGenerator(Rasa):
    def __init__(self):
        pass

    def generate(self, source, lang="en", **kwargs):
        intents = source.get_intents()
        ret = {}
        for intent in intents.values():
            name = self._rasa_name(intent.get("name"))
            ret[name] = intent.responses.get(lang)
        return json.dumps(ret, indent=2)

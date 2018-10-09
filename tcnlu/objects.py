from collections import defaultdict
import jsonpickle, json, re

class NLUFormat:
    def get_name(self):
        raise NotImplementedError("Please Implement this method")

    def get_intents(self):
        raise NotImplementedError("Please Implement this method")
    
    def get_entities(self):
        raise NotImplementedError("Please Implement this method")

class Item:
    def __init__(self, text, name=None, meta=None):
        self.text = text
        self.name = name
        self.meta = meta

    def __repr__(self):
        return "%r (%r, %r)" % (self.text, self.name, self.meta)

class Sample:
    def __init__(self, items = []):
        self.items = items

    def __iter__(self):
        for item in self.items:
            yield item

    def add_item(self, text, name=None, meta=None):
        self.items.append(Item(text, name, meta))

    @property
    def text(self):
        return "".join(x.text for x in self.items)

class Slot():
    def __init__(self, name, dataType, required):
        self.name = name
        self.dataType = dataType
        self.required = required
        self.prompts = defaultdict(list)

    def add_prompt(self, lang, prompt):
        self.prompts[lang].append(prompt)

    def __repr__(self):
        return "%r %r %r %r" % (self.name, self.dataType, self.required, self.prompts)

class Intent:
    def __init__(self):
        self.samples = defaultdict(list)
        self.slots = list()
        self.params = {}
        self.responses = defaultdict(list)

    def add_samples(self, language, samples):
        self.samples[language].extend(samples)

    def add_slot(self, slot):
        self.slots.append(slot)

    def add_responses(self, language, responses):
        if responses:
            self.responses[language].extend(responses)

    def add_response(self, language, response):
        if response:
            self.responses[language].append(response)

    def set_param(self, key, value):
        self.params[key] = value

    def get(self, key):
        return self.params.get(key)

    def __repr__(self):
        return "%r" % self.params

class Response:
    def __init__(self, text, *quick_replies):
        self.text = text
        self.quick_replies = quick_replies

class Entity:
    def __init__(self):
        self.entries = defaultdict(list)
        self.params = {}

    def add_entries(self, language, entries):
        self.entries[language].extend(entries)

    def get_entries(self, language):
        return self.entries[language]

    def set_param(self, key, value):
        self.params[key] = value

    def get(self, key):
        return self.params.get(key)




class Type:
    def __init__(self, name):
        self.name = name

class StandardType(Type):
    def __init__(self, **engines):
        self.engines = engines

    def get(self, engine):
        return self.engines.get(engine)

class CustomType(Type):
    def get(self, engine):
        return self.name

class RegexType(Type):
    def __init__(self, regex):
        self.regex = regex

class StandardTypes:
    all_types = [
        StandardType(dialogflow="sys.ignore", 
                     alexa=None, 
                     rasanlu=None),
        StandardType(dialogflow="sys.language", 
                     alexa="AMAZON.Language", 
                     rasanlu=None),
        StandardType(dialogflow="sys.any", 
                     alexa="AMAZON.LITERAL", 
                     rasanlu=None),
        StandardType(dialogflow="sys.date", 
                     alexa="AMAZON.DATE", 
                     rasanlu=None),
        StandardType(dialogflow="sys.duration", 
                     alexa="AMAZON.DURATION", 
                     rasanlu=None),
        StandardType(dialogflow="sys.number",
                     alexa="AMAZON.NUMBER", 
                     rasanlu=None),
        StandardType(dialogflow="sys.number-integer", 
                     alexa="AMAZON.NUMBER", 
                     rasanlu=None),
        StandardType(dialogflow="sys.location", 
                     alexa = "AMAZON.StreetName",
                     rasanlu=None),
        StandardType(dialogflow="sys.geo-country", 
                     alexa="AMAZON.Country",  
                     rasanlu=None),
        StandardType(dialogflow="sys.geo-city", 
                     alexa="AMAZON.EUROPE_CITY", 
                     rasanlu=None),
        StandardType(dialogflow="sys.email", 
                     alexa="AMAZON.LITERAL", 
                     rasanlu=RegexType(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")),
        StandardType(dialogflow="sys.flight-number",
                     alexa="AMAZON.FOUR_DIGIT_NUMBER",
                     rasanlu=None),
    ]
    @classmethod
    def find(cls, engine, key):
        for t in cls.all_types:
            if t.get(engine) == key:
                return t
        raise Exception("Cannot find type %s for %s" % (key, engine))


class NeutralParser(NLUFormat):
    def __init__(self, path, name="dummy"):
        with open(path) as h:
            data = json.load(h)
            self.name = data.get("name")
            self.intents = jsonpickle.decode(json.dumps(data.get("intents")))
            self.entities = jsonpickle.decode(json.dumps(data.get("entities")))

    def get_name(self):
        return self.name

    def get_intents(self):
        return self.intents
    
    def get_entities(self):
        return self.entities

class NeutralGenerator():
    def __init__(self):
        pass

    def generate(self, source, lang="en"):
        name, intents, entities = source.get_name(), source.get_intents(), source.get_entities()
        return json.dumps({
            "format"   : "neutral",
            "version"  : 1,
            "name"     : name,
            "intents"  : json.loads(jsonpickle.encode(intents)),
            "entities" : json.loads(jsonpickle.encode(entities)),
        }, indent=2)


class ResponsesGenerator():
    def __init__(self):
        pass

    def generate(self, source, lang="en", **kwargs):
        intents = source.get_intents()
        ret = []
        for intent in intents.values():
            name = intent.get("name")
            samples = intent.samples.get(lang)
            if samples:
                #samples = sorted([i.text for i in samples], key=lambda i:len(i))
                best = " | ".join(x.text for x in samples)
            else:
                best = ""
            resp = intent.responses.get(lang)
            for x in filter(lambda x:x is not None, resp):
                ret.append([name, best, re.sub("[\n\r]", "", x.text), " | ".join(x.quick_replies)])
            ret.sort(key=lambda x:x[0])
        return "\n".join("\t".join(i) for i in ret)
        

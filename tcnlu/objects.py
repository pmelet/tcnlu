from collections import defaultdict


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

class Intent:
    def __init__(self):
        self.samples = defaultdict(list)
        self.entities = None
        self.params = {}
        self.responses = defaultdict(list)

    def add_samples(self, language, samples):
        self.samples[language].extend(samples)

    def set_entities(self, entities):
        self.entities = entities

    def add_responses(self, language, responses):
        if responses:
            self.responses[language].extend(responses)

    def set_param(self, key, value):
        self.params[key] = value

    def get(self, key):
        return self.params.get(key)

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

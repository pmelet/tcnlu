from collections import defaultdict

class Item:
    def __init__(self, text, name=None, meta=None):
        self.text = text
        self.name = name
        self.meta = meta

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
        self.responses[language].extend(responses)

    def set_param(self, key, value):
        self.params[key] = value

    def get(self, key):
        return self.params.get(key)

class Entity:
    pass

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

class StandardTypes:
    all_types = [
        StandardType(dialogflow="sys.any", alexa="AMAZON.LITERAL"),
        StandardType(dialogflow="sys.duration", alexa="AMAZON.DURATION"),
        StandardType(dialogflow="sys.number", alexa="AMAZON.NUMBER"),
        StandardType(dialogflow="sys.geo-country", alexa="AMAZON.Country"),
        StandardType(dialogflow="sys.geo-city", alexa="AMAZON.EUROPE_CITY"),
        StandardType(dialogflow="sys.email", alexa="AMAZON.LITERAL"),
    ]
    @classmethod
    def find(cls, engine, key):
        for t in cls.all_types:
            if t.get(engine) == key:
                return t

import os.path, json
from os import listdir
from os.path import isfile, join
from collections import defaultdict
from .tools import get, enforce_list
from .objects import Entity, Intent, Sample, Item, StandardTypes, CustomType, NLUFormat
from pprint import pprint
import zipfile

class DialogFlowV1Parser(NLUFormat):
    def __init__(self, path, name="dummy"):
        self.path = path
        self.name = name
        self.intents, self.entities = None, None
        self.iszipfile = False
        if isfile(path):
            zipfile.ZipFile(path)
            self.iszipfile = True
        
        self._parse_entities()
        self._parse_intents()

    def _parse_entities(self):
        ### TODO : Add a detection mechanism of the format (zip of folder) and use different file reading methods depending on the case.
        entities = defaultdict(Entity)
        entities_path = os.path.join(self.path, "entities")
        for file in listdir(entities_path):
            filename = os.path.join(entities_path, file)
            tocheck = file.rsplit("_", 2)
            with open(filename, encoding="utf8") as h:
                data = json.load(h)
            if len(tocheck)==3 and tocheck[1] == "entries":
                name = tocheck[0]
                language = tocheck[2].split(".")[0]
                entities[name].add_entries(language, data)
            else:
                name = file.rsplit(".",1)[0]
                entities[name].set_param("name", get(data, "name"))
        #pprint(entities)
        self.entities = entities

    def _parse_intents(self):
        ### TODO : Add a detection mechanism of the format (zip of folder) and use different file reading methods depending on the case.
        intents = defaultdict(Intent)
        intents_path = os.path.join(self.path, "intents")
        for file in listdir(intents_path):
            filename = os.path.join(intents_path, file)
            tocheck = file.rsplit("_", 2)
            with open(filename, encoding="utf8") as h:
                data = json.load(h)
            if len(tocheck)==3 and tocheck[1] == "usersays":
                # "usersays" file contains samples
                name = tocheck[0]
                language = tocheck[2].split(".")[0]
                intents[name].add_samples(language, self._extract_samples(data))
            else:
                # intent file, contains metadata : parameters, messages, etc.
                name = file.rsplit(".",1)[0]
                intents[name].set_param("name", get(data, "name"))
                intents[name].set_entities(get(data, "responses.0.parameters"))
                for item in get(data, "responses.0.messages"):
                    intents[name].add_responses(item["lang"], enforce_list(item["speech"]))
        self.intents = intents

    def _extract_samples(self, data):
        return map(self._make_sample, data)

    def _make_sample(self, item):
        """
        Read the sample, to generate as many Items as there are parts in the sample
        """
        return Sample(items = [Item(x.get("text"),x.get("alias"),self._collect_type(x.get("meta"))) \
                               for x in item["data"]])

    def _collect_type(self, meta):
        """
        """
        if meta:
            if meta[1:5] == "sys.":
                return StandardTypes.find("dialogflow", meta[1:])
            return CustomType(meta[1:])


    def get_name(self):
        return self.name
    
    def get_intents(self):
        return self.intents
    
    def get_entities(self):
        return self.entities
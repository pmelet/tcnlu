import os.path, json
from os import listdir
from os.path import isfile, join
from collections import defaultdict
from .tools import get, enforce_list
from .objects import Intent, Sample, Item, StandardTypes, CustomType
from pprint import pprint
import zipfile

class DialogFlowV1Parser:
    def __init__(self, path, name="dummy"):
        self.path = path
        self.name = name
        self.intents, self.entities = None, None
        self.iszipfile = False
        if isfile(path):
            zipfile.ZipFile(path)
            self.iszipfile = True

    def get_name(self):
        return self.name

    def _parse(self):
        if self.intents is None:

            entities = defaultdict(dict)
            entities_path = os.path.join(self.path, "entities")
            for file in listdir(entities_path):
                filename = os.path.join(entities_path, file)
                tocheck = file.rsplit("_", 2)
                with open(filename, encoding="utf8") as h:
                    data = json.load(h)
                if len(tocheck)==3 and tocheck[1] == "entries":
                    name = tocheck[0]
                    language = tocheck[2].split(".")[0]
                    entities[name][language] = data
                else:
                    name = file.rsplit(".",1)[0]
                    entities[name]["info"] = {
                        "name" : get(data, "name"),
                    }
            pprint(entities)
            self.entities = entities

            intents = defaultdict(Intent)
            intents_path = os.path.join(self.path, "intents")
            for file in listdir(intents_path):
                filename = os.path.join(intents_path, file)
                tocheck = file.rsplit("_", 2)
                with open(filename, encoding="utf8") as h:
                    data = json.load(h)
                if len(tocheck)==3 and tocheck[1] == "usersays":
                    name = tocheck[0]
                    language = tocheck[2].split(".")[0]
                    intents[name].add_samples(language, self._extract_samples(data))
                else:
                    name = file.rsplit(".",1)[0]
                    intents[name].set_param("name", get(data, "name"))
                    intents[name].set_entities(get(data, "responses.0.parameters"))
                    for item in get(data, "responses.0.messages"):
                        intents[name].add_responses(item["lang"], enforce_list(item["speech"]))
            self.intents = intents
        return self.intents, self.entities

    def _extract_samples(self, data):
        return map(self._make_sample, data)

    def _make_sample(self, item):
        return Sample(items = [Item(x.get("text"),x.get("alias"),self._collect_type(x.get("meta"))) \
                               for x in item["data"]])

    def _collect_type(self, meta):
        if meta:
            if meta[1:5] == "sys.":
                return StandardTypes.find("dialogflow", meta[1:])
            return CustomType(meta[1:])


    def get_intents(self):
        intents, _ = self._parse()
        return intents
    
    def get_entities(self):
        _, entities = self._parse()
        return entities
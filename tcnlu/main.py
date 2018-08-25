import json, sys, os
from os import listdir
from os.path import isfile, join
import re
from collections import defaultdict
from html import escape
import argparse
import zipfile
import json
from pprint import pprint

UNITS = [
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]

TENS = [
    "ten",
    "twenty",
    "thirty",
    "fourty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
]

GROUPS = [
    "",
    "thousand",
    "million",
    "billion",
    "trillion",
]

def number_as_string_grouped(number):
    stack = []
    if number % 100 >= 20:
        stack.insert(0, TENS[((number % 100) // 10)-1] + " " + number_as_string_grouped(number%10))
    else:
        stack.insert(0, UNITS[number%100-1])        
    if number >= 100:
        stack.insert(0, number_as_string_grouped(number//100) + " hundred")
    return (" ".join(stack))

def number_as_string(number):
    if type(number) == str:
        number = int(number)
    stack = []
    group = 0
    while number > 0:
        appendix = GROUPS[group]
        group += 1
        lit = number_as_string_grouped(number % (10**(3*group)))
        stack.insert(0,lit + " " + appendix)
        number = number // 10**(3*group)
    return (" ".join(stack)).strip()


def transform_numbers(source_text):
    text = source_text
    for m in re.finditer(r"[0-9]+", source_text):
        text = text.replace(m.group(), number_as_string(m.group()))
    return text

def get(data, path, donepath=[], default=None, transform=None, sep=".", verbose=False):
    if verbose : print >>sys.stderr, path, donepath, 
    if data is None:
        return None
    if type(path) != list:
        path = path.split(sep)
    head, tail = path[0], path[1:]
    sub = None

    m = re.match(r"\[(.*)=(.*)\]", head)
    if m:
        key, value = m.group(1), m.group(2)
        if type(data) == list:
            for item in data:
                if type(item) == dict and item.get(key) == value:
                    sub = item
                    break
        else:
            raise ValueError("%s.%s=%s: type(data) == %s" % (sep.join(donepath), key, value, type(data)))        
    else:
        try:
            head_as_int = int(head)
            if type(data) == list:
                sub = data[head_as_int]
            else:
                raise ValueError("%s.%d: type(data) == %s" % (sep.join(donepath), head_as_int, type(data)))
        except ValueError:
            if type(data) == dict:
                sub = data.get(head)
            else:
                raise ValueError("%s.%s: type(data) == %s [%r]" % (sep.join(donepath), head, type(data)))
    if verbose : print >>sys.stderr, "=>", type(sub)
    if len(tail)>0 and sub is not None:
        if verbose : print >>sys.stderr, "recurse"
        sub = get(sub, tail, default=default, donepath=donepath+[head])
        if verbose : print >>sys.stderr, " <= ", sub, default
        if transform:
            try:
                return transform(sub)
            except:
                return default
        return default if sub is None else sub
    if verbose : print >>sys.stderr, "leave", sub, default
    if transform:
        try:
            return transform(sub)
        except:
            return default
    return default if sub is None else sub  


ERROR_INPUT_FORMAT_NOT_DETECTED = 1

DIALOG_FLOW = "DialogFlow"
ALEXA = "Alexa"

DIALOG_FLOW_V1 = (DIALOG_FLOW, 1)
DIALOG_FLOW_V2 = (DIALOG_FLOW, 2)
ALEXA_JSON = (ALEXA, None)

MAP_DIALOG_FLOW_TO_ALEXA = {
    "sys.any" :         "AMAZON.LITERAL",
    "sys.duration" :    "AMAZON.DURATION",
    "sys.number" :      "AMAZON.NUMBER",
    "sys.geo-country" : "AMAZON.Country",
    "sys.geo-city" :    "AMAZON.EUROPE_CITY", #TODO : fix!!
    "sys.email":        "AMAZON.LITERAL",
}

class Alexa:
    def __init__(self):
        pass

    def generate(self, source):
        name, intents, entities = source.get_name(), source.get_intents(), source.get_entities()
        return {
            "interactionModel": {
                "languageModel": {
                    "invocationName": name,
                    "intents": self.generate_intents(intents, entities, add_default=True),
                    "types": self.generate_entities(entities)
                }
            }
        }

    def generate_intents(self, intents, entities, add_default=True):
        ret = []
        for intent in intents.values():
            samples = intent.get("en")
            if not samples:
                continue
            item = {
                "name": self._alexa_name(get(intent, "info.name")),
                "samples": ["".join([self.get_sample_element(item) for item in items]) for items in samples]
            }
            slots = [{"name":alias, "type":meta} for (alias, meta) in self.collect_slots(samples)]
            if slots:
                item["slots"] = slots
            ret.append(item)
        return ret

    _alexa_name_patern = re.compile('[^a-zA-Z0-9_]+')
    def _alexa_name(self, string):
        return transform_numbers(self._alexa_name_patern.sub('', string).lower())

    def _meta(self, item):
        meta = item.get("meta")
        if meta:
            meta = meta[1:]
            if meta[:4] == "sys.":
                meta = MAP_DIALOG_FLOW_TO_ALEXA.get(meta)
                return meta, meta == "AMAZON.LITERAL"
            return self._alexa_name(meta), False

    def collect_slots(self, samples):
        slots = set()
        for sample in samples:
            for item in sample:
                alias = item.get("alias")
                if alias:
                    meta, _ = self._meta(item)
                    slots.add((self._alexa_name(alias), meta))
        return slots

    _alexa_sample_patern = re.compile('[^a-zA-Z0-9_{} ]+')
    def get_sample_element(self, item):
        alias, source_text = item.get("alias"), item.get("text")
        text = transform_numbers(source_text)
        text = self._alexa_sample_patern.sub('', text)
        if alias:
            _, example = self._meta(item)
            if example:
                return " {%s|%s} " % (text, self._alexa_name(alias))
            return " {%s} " % self._alexa_name(alias)
        return text

    def generate_entities(self, entities):
        ret = []
        for entity in entities.values():
            ret.append({
                "name": self._alexa_name(get(entity, "info.name")),
                "values": [{"name": entry} for entry in get(entity, "en")]
            })
        return ret

class DialogFlow_1:
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

            intents = defaultdict(dict)
            intents_path = os.path.join(self.path, "intents")
            for file in listdir(intents_path):
                filename = os.path.join(intents_path, file)
                tocheck = file.rsplit("_", 2)
                with open(filename, encoding="utf8") as h:
                    data = json.load(h)
                if len(tocheck)==3 and tocheck[1] == "usersays":
                    name = tocheck[0]
                    language = tocheck[2].split(".")[0]
                    intents[name][language] = [ item["data"] for item in data ]
                else:
                    name = file.rsplit(".",1)[0]
                    intents[name]["info"] = {
                        "name" : get(data, "name"),
                        "entities" : get(data, "parameters")
                    }
            #pprint(intents.get("1-Baggage"))
            #self.intents = {"1-Baggage": intents.get("1-Baggage") }
            self.intents = intents
        return self.intents, self.entities

    def get_intents(self):
        intents, _ = self._parse()
        return intents
    
    def get_entities(self):
        _, entities = self._parse()
        return entities

def format_stats(format, version):
    return 0, 0

FORMAT_NOT_DETECTED = (None, None)

def detect_folder_structure(folders):
    if folders.get("agent.json") == "" \
       and type(folders.get("intents"))==dict \
       and type(folders.get("entities"))==dict :
        return DIALOG_FLOW_V1
    return FORMAT_NOT_DETECTED

def build_zipfile_structure(archive):
    ret = {}
    for name in archive.namelist():
        items = name.split("/")
        current = ret
        for index, item in enumerate(items):
            if item == "":
                continue
            if index == len(items)-1:
                current.setdefault(item, "")
            else:
                current.setdefault(item, {})
            current = current.get(item)
    return ret

def detect_zipfile(archive):
    folder_structure = build_zipfile_structure(archive)
    return detect_folder_structure(folder_structure)

def detect_jsonfile(jsonfile):
    if "interactionModel" in jsonfile.keys():
        return ALEXA_JSON
    return FORMAT_NOT_DETECTED

def detect_plainfile(plainfile):
    try:
        return detect_jsonfile(json.load(open(plainfile)))
    except Exception:
        pass
    return FORMAT_NOT_DETECTED

def build_folder_structure(folder):
    ret = {}
    for entry in listdir(folder):
        filename = os.path.join(folder, entry)
        if isfile(filename):
            ret[entry] = ""
        else:
            ret[entry] = build_folder_structure(filename)
    return ret

def detect_folder(folder):
    folder_structure = build_folder_structure(folder)
    return detect_folder_structure(folder_structure)

def detect(args):
    if isfile(args.ifile):
        try:
            format, version = detect_zipfile(zipfile.ZipFile(args.ifile))
        except zipfile.BadZipFile:
            format, version = detect_plainfile(args.ifile)
    else:
        format, version = detect_folder(args.ifile)
    
    if format is None:
        sys.exit(ERROR_INPUT_FORMAT_NOT_DETECTED)
    else:
        print(format, version, format_stats(format, version))
        sys.exit(0)

def check(args):
    print(args)

def transform(args):
    from_object = DialogFlow_1(args.ifile, name="pierre etienne")
    to_object = Alexa()
    data = json.dumps(to_object.generate(from_object), indent=2)
    with open(args.ofile, "w") as h:
        h.write(data)

def test(args):
    pprint(number_as_string(1))
    pprint(number_as_string(11))
    pprint(number_as_string(22))
    pprint(number_as_string(122))
    pprint(number_as_string(1234))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("function")
    parser.add_argument("ifile", nargs="?")
    parser.add_argument("ofile", nargs="?")
    args = parser.parse_args()
    pprint(args)
    globals().get(args.function)(args)
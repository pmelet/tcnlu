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
from .humans import numbers as transform_numbers
from .tools import get
from .dialogflow import DialogFlowV1Parser
from .alexa import AlexaGenerator, AlexaResponseGenerator

ERROR_INPUT_FORMAT_NOT_DETECTED = 1

DIALOG_FLOW = "DialogFlow"
ALEXA = "Alexa"

DIALOG_FLOW_V1 = (DIALOG_FLOW, 1)
DIALOG_FLOW_V2 = (DIALOG_FLOW, 2)
ALEXA_JSON = (ALEXA, None)


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

def detect_path(path):
    if isfile(path):
        try:
            return detect_zipfile(zipfile.ZipFile(path))
        except zipfile.BadZipFile:
            return detect_plainfile(path)
    else:
        return detect_folder(path)
    return None, None

def detect(args):
    format, version = detect_path(args.ifile)
    if format is None:
        sys.exit(ERROR_INPUT_FORMAT_NOT_DETECTED)
    else:
        print(format, version)
        sys.exit(0)

def check(args):
    print(args)

FORMAT_HELPERS = {
    DIALOG_FLOW_V1 : {
        "parser": DialogFlowV1Parser,
        "generators": None
    },
    ALEXA_JSON : {
        "parser": None,
        "generators": (AlexaGenerator, AlexaResponseGenerator)
    }
}


def transform(args):
    intents = None
    responses = None
    if len(args.ofile) > 0:
        intents = args.ofile[0]
    if len(args.ofile) > 1:
        responses = args.ofile[1]

    from_format = detect_path(args.ifile)
    print(from_format)
    parser = get(FORMAT_HELPERS[from_format], "parser")
    from_object = parser(args.ifile, name="etraveli")

    #TODO : should be based on "output format". Harcoded for now
    if intents:
        to_object = AlexaGenerator()
        data = json.dumps(to_object.generate(from_object), indent=2)
        with open(intents, "w") as h:
            h.write(data)

    if responses:
        to_object = AlexaResponseGenerator()
        data = json.dumps(to_object.generate(from_object), indent=2)

        with open(responses, "w") as h:
            h.write(data)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("function")
    parser.add_argument("ifile", nargs="?")
    parser.add_argument("ofile", nargs="*")
    args = parser.parse_args()
    globals().get(args.function)(args)
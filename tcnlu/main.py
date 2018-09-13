import json, sys, os
from os import listdir
from os.path import isfile, join
import re
from collections import defaultdict
from html import escape
import zipfile
import json
from pprint import pprint
from tabulate import tabulate
import argh
from argh import arg
from argh import EntryPoint

from .humans import numbers as transform_numbers
from .tools import get
from .dialogflow import DialogFlowV1Parser
from .alexa import AlexaGenerator, AlexaResponseGenerator

app = EntryPoint('tcnlu')

ERROR_INPUT_FORMAT_NOT_DETECTED = 1

DIALOG_FLOW = "DialogFlow"
ALEXA = "Alexa"

DIALOG_FLOW_V1 = (DIALOG_FLOW, 1)
DIALOG_FLOW_V2 = (DIALOG_FLOW, 2)
ALEXA_JSON = (ALEXA, None)


def format_format(format, version):
    if version is None:
        return format
    return "%s:%s" % (format, version)

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

@app
def detect(path):
    format, version = detect_path(path)
    if format is None:
        sys.exit(ERROR_INPUT_FORMAT_NOT_DETECTED)
    else:
        print(format, version)
        sys.exit(0)

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

@app
def formats():
    tab = []
    for helper, funcs in FORMAT_HELPERS.items():
        format, version = helper
        tab.append([format, version, funcs.get("parser") is not None, funcs.get("generators") is not None])
    print(tabulate(tab, headers=["format", "version", "read", "write"]))

@arg('ifile', help='input file')
@arg('--of', help='output format and version. format[:version]')
@arg('ofiles', nargs='+', help='output files')
@app
def transform(ifile : "input file", ofiles, of=None):
    "Generate training file in a format from training file in another."

    # detect input format, and find parser
    from_format = detect_path(ifile)
    parser = get(FORMAT_HELPERS[from_format], "parser")
    from_object = parser(ifile, name="etraveli")

    #TODO : should be based on "output format". Harcoded for now
    generators = get(FORMAT_HELPERS[ALEXA_JSON], "generators")
    for (generator, ofile) in zip(generators, ofiles):
        to_object = generator()
        data = json.dumps(to_object.generate(from_object), indent=2)
        with open(ofile, "w") as h:
            h.write(data)

def main():
    #parser = argh.ArghParser()
    #parser.add_commands([formats, detect, transform])
    #parser.dispatch()
    app()

import json, sys, os
from os import listdir
from os.path import isfile, join
import zipfile


DIALOG_FLOW = "DialogFlow"
ALEXA = "Alexa"
RASANLU = "RASANlu"

DIALOG_FLOW_V1 = (DIALOG_FLOW, None, 1)
DIALOG_FLOW_V2 = (DIALOG_FLOW, None, 2)
ALEXA_JSON = (ALEXA, None, None)
RASANLU_JSON = (RASANLU, "json", None)
RASANLU_MKD = (RASANLU, "markdown", None)

FORMAT_NOT_DETECTED = (None, None, None)


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

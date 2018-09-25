import json, sys, os
from os import listdir
from os.path import isfile, join
import zipfile

FORMAT_ZIP = "zip"
FORMAT_FOLDER = "folder"
FORMAT_JSON = "json"
FORMAT_MARKDOWN = "markdown"

DIALOG_FLOW = "DialogFlow"
ALEXA = "Alexa"
RASANLU = "RASANlu"
NEUTRAL = "Neutral"

DIALOG_FLOW_V1_FOLDER = (DIALOG_FLOW, FORMAT_FOLDER, 1)
DIALOG_FLOW_V1_ZIP = (DIALOG_FLOW, FORMAT_ZIP, 1)
ALEXA_JSON = (ALEXA, None, None)
RASANLU_JSON = (RASANLU, FORMAT_JSON, None)
RASANLU_MKD = (RASANLU, FORMAT_MARKDOWN, None)
NEUTRAL_JSON_1 = (NEUTRAL, FORMAT_JSON, 1)

FORMAT_NOT_DETECTED = (None, None, None)


def detect_folder_structure(folders, format):
    if folders.get("agent.json") == "" \
       and type(folders.get("intents"))==dict \
       and type(folders.get("entities"))==dict :
        return (DIALOG_FLOW, format, 1)
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
    return detect_folder_structure(folder_structure, FORMAT_ZIP)

def detect_jsonfile(jsonfile):
    keys = jsonfile.keys()
    if "interactionModel" in keys:
        return ALEXA_JSON
    if "format" in keys and "version" in keys:
        return (NEUTRAL, FORMAT_JSON, jsonfile.get("version"))
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
    return detect_folder_structure(folder_structure, FORMAT_FOLDER)


def detect_path(path):
    if isfile(path):
        try:
            return detect_zipfile(zipfile.ZipFile(path))
        except zipfile.BadZipFile:
            return detect_plainfile(path)
    else:
        return detect_folder(path)
    return None, None

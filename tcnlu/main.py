import json, sys, os
from os import listdir
import re
from collections import defaultdict, Iterable
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
from .rasa import RasaMarkDownGenerator, RasaResponseGenerator
from .exceptions import TcnluError
from .exceptions import ERROR_INPUT_FORMAT_NOT_DETECTED, ERROR_OUTPUT_FORMAT_NOT_DETECTED
from .formats import DIALOG_FLOW_V1, ALEXA_JSON, FORMAT_NOT_DETECTED, RASANLU_JSON, RASANLU_MKD
from .formats import detect_path

app = EntryPoint('tcnlu')

FORMAT_HELPERS = {
    DIALOG_FLOW_V1 : {
        "parser": DialogFlowV1Parser,
        "generators": None
    },
    ALEXA_JSON : {
        "parser": None,
        "generators": (AlexaGenerator, AlexaResponseGenerator)
    },
    RASANLU_JSON : {
        "parser": None,
        "generators": None
    },
    RASANLU_MKD : {
        "parser": None,
        "generators": (RasaMarkDownGenerator, RasaResponseGenerator)
    },
}

def parse_format(input):
    """
    there are several ways to declare a format:
    - provider:format:version, if provider have different formats with different versions
    - provider:version, if provider have one format with different versions
    - provider:format, if provider have various formats, unversioned
    """
    if input is None:
        return None
    x = input.split(":")
    input_provider = x[0]
    input_details = x[1:]

    best_helper = None
    match_helper = -1

    for helper, _ in FORMAT_HELPERS.items():
        provider, format, version = helper

        if (provider.lower() != input_provider.lower()):
            # useless
            continue        
        match = 1
        for input_detail in input_details:
            # iterate on additional info, and try to match
            match += (format == input_detail or str(format) == input_detail)
            match += (version == input_detail or str(version) == input_detail)

        if match > match_helper:
            match_helper = match
            best_helper = helper
    
    return best_helper

@arg('path', help='path of file or folder to analyze')
@app
def detect(path):
    "Detect format and variant, outputing the result on stdout."

    provider, format, version = detect_path(path)
    if provider is None:
        sys.exit(ERROR_INPUT_FORMAT_NOT_DETECTED)
    else:
        formats_table([(provider, format, version)])
        sys.exit(0)

@app
@arg('formats', nargs='*', help='detect formats and show details')
def formats(formats):
    "Display recognized formats."

    filter = FORMAT_HELPERS.keys()
    if formats:    
        filter = []
        for format in formats:
            f = parse_format(format)
            if f:
                filter.append(f)
    formats_table(filter)

def formats_table(formats, header=True):
    tab = [("provider", "format", "version", "read", "write")]
    for helper in formats:
        funcs = FORMAT_HELPERS.get(helper)
        provider, format, version = helper
        tab.append([provider, format, version, funcs.get("parser") is not None, funcs.get("generators") is not None])
    if header:
        print(tabulate(tab, tablefmt="fancy_grid", headers="firstrow"))
    else:
        print(tabulate(tab, tablefmt="plain"))

@arg('ifile', help='input file')
@arg('ofiles', nargs='+', help='output files')
@arg('--lang', help='language', required=False)
@arg('--of', help='output format and version. format[:version]', required=True)
@app
def transform(ifile : "input file", ofiles, of=None, lang="en", name="default name"):
    "Generate training file in a format from training file in another."

    # detect input format, and find parser
    from_format = detect_path(ifile)
    parser = get(FORMAT_HELPERS[from_format], "parser")
    from_object = parser(ifile, name=name)

    to_format = parse_format(of)
    if to_format is None:
        raise TcnluError(ERROR_OUTPUT_FORMAT_NOT_DETECTED)
    generators = get(FORMAT_HELPERS[to_format], "generators")
    if not isinstance(generators, Iterable):
        generators = [ generators ]
    for (generator, ofile) in zip(generators, ofiles):
        to_object = generator()
        data = to_object.generate(from_object, lang=lang)
        if ofile == "-":
            print (data)
        else:
            with open(ofile, "w") as h:
                h.write(data)

def main():
    try:
        app()
    except TcnluError as e:
        print(e)
        sys.exit(e.error_code)

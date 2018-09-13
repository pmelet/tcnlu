# Installation
This package is still in development.

    git clone https://github.com/pmelet/tcnlu.git
    cd tcnlu
    pip install -e .

# User manual

## List formats

    tcnlu formats

Display recognized formats. Columns:

 - format  : name of the format
 - version : version of the format, if applicable
 - read    : format can be read by the tool
 - write   : format can be written by the tool

```
> tcnlu formats
format        version  read    write
----------  ---------  ------  -------
DialogFlow          1  True    False
Alexa                  False   True
```

## Detect file format
    tcnlu detect [path]

Detects format and variant, outputing the result on stdout.

Returns 0 if detected and valid, else return error code

 - 1 = input format is not recognized
 - 2 = input file was analyzed and is corrupted

## Format transcoding
    tcnlu transform --of <format>[:<variant>] input output [output]

Generate training file in a format from training file in another.

### Alexa

    tcnlu transform <input file in another format> <alexa json> [responses json]
with:

 - `alexa json`: a file that can be imported into alexa
 - `responses json`: a file that can be used to generate responses in a lambda function
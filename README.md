# Installation
## pip

    pip install tcnlu

## Development

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
╒════════════╤══════════╤═══════════╤════════╤═════════╕
│ provider   │ format   │   version │ read   │ write   │
╞════════════╪══════════╪═══════════╪════════╪═════════╡
│ DialogFlow │          │         1 │ True   │ False   │
├────────────┼──────────┼───────────┼────────┼─────────┤
│ Alexa      │          │           │ False  │ True    │
├────────────┼──────────┼───────────┼────────┼─────────┤
│ RASANlu    │ json     │           │ False  │ False   │
├────────────┼──────────┼───────────┼────────┼─────────┤
│ RASANlu    │ markdown │           │ False  │ True    │
╘════════════╧══════════╧═══════════╧════════╧═════════╛
```

## Detect file format
    tcnlu detect [path]

Detects format and variant, outputing the result on stdout.

Returns 0 if detected and valid, else return error code

 - 1 = input format is not recognized
 - 2 = input file was analyzed and is corrupted

## Format transcoding
    tcnlu transform input --of <format>[:<variant>] output [output ...]

Generate training file in a format from training file in another.

Returns 0 if detected and valid, else return error code

 - 1 = input format is not recognized
 - 10 = output format is not recognized

### Alexa

    tcnlu transform <input file in another format> --of alexa <alexa json> [responses json]
with:

 - `alexa json`: a file that can be imported into alexa
 - `responses json`: a file that can be used to generate responses in a lambda function. Lambda function is available in `resources/alexa`

 ### Rasa

    tcnlu transform <input file in another format> --of rasanlu:[markdown or json] <rasa file> [responses json]
with:

 - `rasa file`: a file that can be imported into rasa nlu
 - `responses json`: a file that can be used to generate responses
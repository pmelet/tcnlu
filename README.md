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
│ DialogFlow │ folder   │         1 │ True   │ False   │
├────────────┼──────────┼───────────┼────────┼─────────┤
│ DialogFlow │ zip      │         1 │ True   │ False   │
├────────────┼──────────┼───────────┼────────┼─────────┤
│ Alexa      │          │           │ False  │ True    │
├────────────┼──────────┼───────────┼────────┼─────────┤
│ RASANlu    │ json     │           │ False  │ False   │
├────────────┼──────────┼───────────┼────────┼─────────┤
│ RASANlu    │ markdown │           │ False  │ True    │
├────────────┼──────────┼───────────┼────────┼─────────┤
│ Neutral    │ json     │         1 │ True   │ True    │
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

```
usage: tcnlu transform [-h] --of OF [--lang LANG] [--name NAME] [--no-literal]
                       ifile ofiles [ofiles ...]

Generate training file in a format from training file in another.

positional arguments:
  ifile         input file
  ofiles        output files

optional arguments:
  -h, --help    show this help message and exit
  --of OF       output format and version. format[:version] (default: -)
  --lang LANG   language (default: 'en')
  --name NAME   Agent name (default: 'default name')
  --no-literal  For alexa: reject intents if that would contain AMAZON.LITERAL
                (necessary if using prompts) (default: False)
```

Returns 0 if detected and valid, else return error code

 - 1 = input format is not recognized
 - 10 = output format is not recognized

### Output files
####Alexa

 - `alexa json`: a file that can be imported into alexa
 - `responses json`: a file that can be used to generate responses in a lambda function. Lambda function is available in `resources/alexa`

#### Rasa

 - `rasa file`: a file that can be imported into rasa nlu
 - `responses json`: a file that can be used to generate responses in application. Test script is available in `resources/rasanlu`
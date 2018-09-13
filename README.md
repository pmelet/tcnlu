# Installation
This package is still in development.

    git clone https://github.com/pmelet/tcnlu.git
    cd tcnlu
    pip install -e .

# User manual
## Detect file format
    tcnlu detect [path]

Detects format and variant, outputing the result on stdout.

Returns 0 if detected and valid, else return error code (see 'check')

 - 1 = input format is not recognized
 - 2 = input file was analyzed and is corrupted

## Format transcoding
    tcnlu transform [--input-format <format>[:<variant>]] --output-format <format>[:<variant>] input output [output]

Generate training file in a format from training file in another.

 - input-format is optional (should be detected)
 - output-format is mandatory

**Note**: for now, `dialogflow v1 folder -> alexa` is hardcoded. No need to try other formats. Thus, `output-format` is in fact optional.

    tcnlu transform <dialogflow unzipped folder> <alexa json> [responses json]
with:

 - `dialogflow unzipped folder`: unzip the file exporter from dialogflow
 - `alexa json`: a file that can be imported into alexa
 - `responses json`: a file that can be used to generate responses in a lambda function
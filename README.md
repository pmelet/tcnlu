# tcnlu

> tcnlu detect [path]
    detects format and variant
    return 0 if detected and valid, else return error code (see 'check')
        1 = input format is not recognized
        2 = input file was analyzed and is corrupted


> tcnlu transform [--input-format <format>[:<variant>]] --output-format <format>[:<variant>] input output [output]
    generate training file in a format from training file in another
    input-format is optional (should be detected)
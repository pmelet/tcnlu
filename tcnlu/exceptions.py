ERROR_INPUT_FORMAT_NOT_DETECTED = 1
ERROR_OUTPUT_FORMAT_NOT_DETECTED = 10

ERRORS = {
    ERROR_INPUT_FORMAT_NOT_DETECTED:  "input format is not recognized",
    ERROR_OUTPUT_FORMAT_NOT_DETECTED: "output format is not recognized",
}

class TcnluError(Exception):
    def __init__(self, error_code):
        super(TcnluError, self).__init__(ERRORS.get(error_code))
        self.error_code = error_code
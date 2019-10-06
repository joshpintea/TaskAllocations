from abc import abstractmethod

import os
import re


class ValidateExtension:
    def __init__(self):
        self.valid_extension = ['.tan', '.txt', '.csv', '.xls']

    def validate(self, file_path):
        _, extension = os.path.splitext(file_path)
        if extension not in self.valid_extension:
            raise Exception("Invalid file extension")


class LineValidation:
    def __init__(self):
        self.comment = re.compile("^\s*\/\/[a-zA-Z0-9 (),]*[.]?|^\s*$")
        self.numbers_in_line = re.compile("^[0-9]*,-?[0-9]*(\.[0-9])?$")
        self.keywords = [
            re.compile("^LIMITS-TASKS,[0-9]*,[0-9]*$"),
            re.compile("^LIMITS-PROCESSORS,[0-9]*,[0-9]*$"),
            re.compile("^LIMITS-PROCESSOR-FREQUENCIES,[0-9]*(\.[0-9]*)?,[0-9]*(\.[0-9]*)?$"),
            re.compile("^PROGRAM-MAXIMUM-DURATION,[0-9]*(\.[0-9])?$"),
            re.compile("^RUNTIME-REFERENCE-FREQUENCY,[0-9]*(\.[0-9])?$"),
            re.compile("^PROGRAM-TASKS,[0-9]*$"),
            re.compile("^PROGRAM-PROCESSORS,[0-9]*$"),
            re.compile("^TASK-ID,RUNTIME$"),
            re.compile("^PROCESSOR-ID,FREQUENCY$"),
            re.compile("^COEFFICIENT-ID,VALUE$"),
            re.compile("^DEFAULT-LOGFILE,\"(\\\\?([^\\/]*[\\/])*)([^\\/]+)\"")
        ]

    def validate(self, line):
        comment_and_numbers = (self.comment.fullmatch(line) is not None) \
                              or (self.numbers_in_line.fullmatch(line) is not None)

        keywords_in_line = False

        for regex in self.keywords:
            keywords_in_line |= (regex.fullmatch(line) is not None)

        return comment_and_numbers or keywords_in_line


class ValidateFile:
    def validate(self, file_path):
        if not os.path.isfile(file_path):
            raise Exception("File not found")

        # check extension
        validate_extension = ValidateExtension()
        validate_extension.validate(file_path)

        #check content
        file = open(file_path)
        content = file.read()
        lines = content.split("\n")
        file.close()

        line_validation = LineValidation()
        lines_valid = [line_validation.validate(line) for line in lines]

        content_is_valid = all([val is True for val in lines_valid])
        if not content_is_valid:
            raise Exception("File is corrupted")


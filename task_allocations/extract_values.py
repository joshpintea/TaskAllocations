import re


class ExtractValues:
    def __init__(self):
        self.keywords = [
            "LIMITS-TASKS",
            "LIMITS-PROCESSORS",
            "LIMITS-PROCESSOR-FREQUENCIES",
            "PROGRAM-MAXIMUM-DURATION",
            "PROGRAM-TASKS",
            "PROGRAM-PROCESSORS",
            "RUNTIME-REFERENCE-FREQUENCY"
        ]

    def _check_valid_limits(self, values, key):
        if values[key][0] > values[key][1]:
            raise Exception("Lower bound should be smaller than upper bound for {}".format(key))

    def _check_limits(self, values, key_limit, key):
        if not values[key_limit][0] <= values[key] <= values[key_limit][1]:
            raise Exception("Value of {} is not in [{}, {}]".format(key, values[key_limit][0], values[key_limit][1]))

    def extract(self, file_path):
        file = open(file_path, 'r')
        file_content = file.read()
        lines = file_content.split("\n")

        line_regex = [re.compile("^{}".format(key)) for key in self.keywords]

        values = {}

        tasks_index, processor_frequencies_index, coeff_index = -1, -1, -1

        for i, line in enumerate(lines):
            for key, regex in zip(self.keywords, line_regex):
                if regex.match(line):
                    try:
                        vals = [int(ch) for ch in line.split(',')[1:]]
                    except ValueError:
                        vals = [float(ch) for ch in line.split(',')[1:]]

                    if len(vals) == 1:
                        values[key] = vals[0]
                    else:
                        values[key] = vals

            if line.startswith("TASK-ID,RUNTIME"):
                tasks_index = i + 1

            if line.startswith("PROCESSOR-ID,FREQUENCY"):
                processor_frequencies_index = i + 1

            if line.startswith("COEFFICIENT-ID,VALUE"):
                coeff_index = i + 1

        keys = [key for key in values.keys()]

        if not len(keys) == len(self.keywords):
            raise Exception("There are missing {}".format(list(set(self.keywords) - set(keys))))

        for key in self.keywords[0:3]:
            self._check_valid_limits(values, key)

        self._check_limits(values, "LIMITS-TASKS", "PROGRAM-TASKS")
        self._check_limits(values, "LIMITS-PROCESSORS", "PROGRAM-PROCESSORS")

        tasks, processors_frequencies, coeff = [], [], []
        for line in lines[tasks_index:tasks_index + values['PROGRAM-TASKS']]:
            tasks.append(float(line.split(",")[1]))

        for line in lines[processor_frequencies_index: processor_frequencies_index + values['PROGRAM-PROCESSORS']]:
            processors_frequencies.append(float(line.split(",")[1]))

        for line in lines[coeff_index: coeff_index + 3]:
            coeff.append(float(line.split(",")[1]))

        values['TASKS_RUNTIME'] = tasks
        values['PROCESSORS_FREQUENCIES'] = processors_frequencies
        values['COEFF'] = coeff

        # check if frequencies are in the limits

        for frequency in values['PROCESSORS_FREQUENCIES']:
            if not values['LIMITS-PROCESSOR-FREQUENCIES'][0] <= frequency <= values['LIMITS-PROCESSOR-FREQUENCIES'][1]:
                raise Exception("Value of {} frequency is not in [{}, {}]"
                                .format(frequency, values['LIMITS-PROCESSOR-FREQUENCIES'][0], values['LIMITS-PROCESSOR-FREQUENCIES'][1]))

        return values




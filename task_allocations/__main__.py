from task_allocations.file_validations import ValidateFile
from task_allocations.extract_values import ExtractValues
from task_allocations.task_allocations import Approach_1, Approach_2

import sys
import os


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("usage python -m task_allocations [file_path] [approach_id]")
        sys.exit(-1)

    file_path = sys.argv[1]
    file_name,_ = os.path.splitext(file_path)
    file_name_out = "{}.tan".format(file_name)

    approach_id = 1
    try:
        approach_id = int(sys.argv[2])
        if approach_id not in [1, 2]:
            approach_id = 1
    except Exception:
        pass

    file_validation = ValidateFile()
    extract_values = ExtractValues()

    try:
        file_validation.validate(file_path)
        values = extract_values.extract(file_path)
        if approach_id == 1:
            task_allocations = Approach_1(values)
        else:
            task_allocations = Approach_2(values)

        task_allocations.allocate_tasks()
        task_allocations.write_output(file_name_out=file_name_out, config_name=file_path)
    except Exception as exp:
        print(exp)
        sys.exit(-1)
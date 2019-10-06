from abc import abstractmethod

import numpy as np


class TaskAllocations:
    def __init__(self, values):
        self.program_maximum_duration = values['PROGRAM-MAXIMUM-DURATION']
        self.runtime_reference_frequency = values['RUNTIME-REFERENCE-FREQUENCY']
        self.processors = values['PROCESSORS_FREQUENCIES']
        self.tasks = values['TASKS_RUNTIME']
        self.coeff = values['COEFF']
        self.result = {
            'time': -1,
            'allocation_table': np.zeros((len(self.processors), len(self.tasks)))
        }

        self.processors_to_task_runtime = np.zeros((len(self.processors), len(self.tasks)),
                                                   dtype=float)

    def _prepocess(self, sort=True):
        self.tasks = [{'id': i, 'val': val} for i, val in enumerate(self.tasks)]
        self.processors = [{'id': i, 'frequency': val, 'time': 0.0, 'energy':0.0} for i, val in
                           enumerate(self.processors)]

        if sort:
            self.processors = sorted(self.processors, key=lambda i: i['frequency'],
                                     reverse=True)
            self.tasks = sorted(self.tasks, key=lambda i: i['val'], reverse=True)

        for processor in self.processors:
            for task in self.tasks:
                time = (self.runtime_reference_frequency * task['val']) / processor['frequency']
                self.processors_to_task_runtime[processor['id']][task['id']] = time

    def _invalid_input(self):
        for task in self.tasks:
            runtimes = self.processors_to_task_runtime[:, task['id']]
            runtimes_smaller_than_duration = [val <= self.program_maximum_duration for val in runtimes]

            valid = False
            for value in runtimes_smaller_than_duration:
                valid |= value
            if not valid:
                raise Exception("Task {} cannot be allocated".format(task['id']))

    def write_output(self, file_name_out, config_name):
        file_out = open(file_name_out, "w")

        print("// The name of the configuration file.", file=file_out)
        print("CONFIGURATION,\"{}\"\n".format(config_name), file=file_out)
        print("//The number of tasks and processors per allocation.", file=file_out)
        print("TASKS,{}".format(len(self.tasks)), file=file_out)
        print("PROCESSORS,{}\n".format(len(self.processors)), file=file_out)

        print("//The number of allocations in this file.", file=file_out)
        print("ALLOCATIONS,1\n", file=file_out)

        print("// The set of allocations.", file=file_out)
        print("// The ith row is the allocation of tasks to the ith processor.", file=file_out)
        print("// The jth column is the allocation of the jth task to a processor.", file=file_out)
        print("ALLOCATION-ID,1", file=file_out)

        for l in self.result['allocation_table']:
            list_as_string = ','.join(str(int(v)) for v in l)
            print(list_as_string, file=file_out)

    @abstractmethod
    def allocate_tasks(self):
        pass

    def compute_energy(self, frequency, time):
        return (self.coeff[2] * frequency * frequency + self.coeff[1] * frequency + self.coeff[0]) * time

    def print_solution(self):
        for processor in self.processors:
            print(processor)

        print(self.result['time'])
        print(self.result['allocation_table'])


class Approach_1(TaskAllocations):
    def allocate_tasks(self):
        super()._prepocess()

        tasks_completed, processors_to_task = [], []
        tasks_left, task_right = 0, len(self.tasks) - 1

        processors_index = 0
        while tasks_left <= task_right:
            if processors_index == len(self.processors):
                raise Exception("Could not allocate tasks with the given processors and the program maximum duration")

            # going from the longest duration of the task to the smallest
            while tasks_left <= task_right:
                time = (self.runtime_reference_frequency * self.tasks[tasks_left]['val']) / \
                       self.processors[processors_index]['frequency']
                if self.processors[processors_index]['time'] + time <= self.program_maximum_duration:
                    self.processors[processors_index]['time'] += time
                    processors_to_task.append((self.processors[processors_index]['id'],
                                               self.tasks[tasks_left]['id']))
                    tasks_left += 1
                else:
                    break

            # going from the smallest duration of the task to the longest
            while tasks_left <= task_right:
                time = (self.runtime_reference_frequency * self.tasks[task_right]['val']) / \
                       self.processors[processors_index]['frequency']
                if self.processors[processors_index]['time'] + time <= self.program_maximum_duration:
                    self.processors[processors_index]['time'] += time
                    processors_to_task.append((self.processors[processors_index]['id'],
                                               self.tasks[task_right]['id']))

                    task_right -= 1
                else:
                    break

            processors_index += 1

        for processor_id, task_id in processors_to_task:
            self.result['allocation_table'][processor_id][task_id] = 1

        for processor in self.processors:
            processor['energy'] = super().compute_energy(processor['frequency'], processor['time'])

        self.result['time'] = max([processor['time'] for processor in self.processors])

        self.print_solution()

class Approach_2(TaskAllocations):

    def _allocate_task(self, visited_task: list, processors_to_task: list, processors_time: np.ndarray, best_solutions):
        if len(visited_task) == len(self.tasks):
            max_time = max(processors_time)
            if max_time < best_solutions['time']:
                best_solutions['time'] = max_time
                best_solutions['sol'] = processors_to_task
            return

        if best_solutions['time'] < self.program_maximum_duration:
            return

        for processor in self.processors:
            for task in self.tasks:
                if task['id'] not in visited_task:
                    time = self.processors_to_task_runtime[processor['id']][task['id']]
                    if processors_time[processor['id']] + time <= self.program_maximum_duration:
                        visited_task_new, processors_to_task_new = visited_task.copy(), processors_to_task.copy()
                        processors_time_new = processors_time.copy()

                        visited_task_new.append(task['id'])
                        processors_time_new[processor['id']] += time
                        processors_to_task_new.append((processor['id'], task['id']))

                        self._allocate_task(visited_task_new,
                                            processors_to_task_new,
                                            processors_time_new,
                                            best_solutions)

    def allocate_tasks(self):
        super()._prepocess(sort=False)
        super()._invalid_input()

        best_solution = {
            'time': self.program_maximum_duration + 1,
            'sol': []
        }

        processors_time = np.zeros(len(self.processors), dtype=float)
        self._allocate_task([], [], processors_time, best_solution)

        self.result['time'] = best_solution['time']

        for processor_id, task_id in best_solution['sol']:
            for processor in self.processors:
                if processor['id'] == processor_id:
                    processor['time'] += self.processors_to_task_runtime[processor_id][task_id]

            self.result['allocation_table'][processor_id][task_id] = 1

        for processor in self.processors:
            processor['energy'] = super().compute_energy(processor['frequency'], processor['time'])

        super().print_solution()
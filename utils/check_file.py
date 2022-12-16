import copy
import os
import subprocess

from utils.__init__ import *

terminal_commands = {
    "c": [["gcc", "file", "-o", "output_file"],  ["output_file"]],
    "cpp": [["g++", "file", "-o", "output_file"], ["output_file"]],
    "java": [["javac", "file", "-d", "output_dir"],  ["java", "file"]],
    "py": [["python3", "file"]],
}

class CheckFile:
    def __init__(self):
        self.file_name = None
        self.dir_name = None
        self.test_input = None
        self.test_output = None
        super().__init__()

    def set_file_name(self, file_name):
        self.file_name = file_name
    def get_file_name(self):
        return self.file_name

    def set_folder(self, dir_name):
        self.dir_name = dir_name
    def get_folder(self):
        return self.dir_name

    def set_test_cases(self, test_input, test_output):
        self.test_input = test_input
        self.test_output = test_output
    def get_test_cases(self):
        return self.test_input, self.test_output


    def run_test(self):
        details =  [self.file_name, self.dir_name, self.test_input, self.test_output]
        if None in details:
            print("Please fill all the required details")
            return []
        file_path = os.path.join(self.dir_name, self.file_name)
        compile_folder = os.path.join(self.dir_name, "compiled")


        extension = self.file_name.split(".")[-1].lower()
        execute_command = []

        def fill_fields_in_command(array):
            array = replace(array, "file", file_path)
            array = replace(array, "dir", self.dir_name)
            array = replace(array, "output_dir", compile_folder)
            output_file = os.path.join(compile_folder, self.file_name.split(".")[0] + ".out")
            array = replace(array, "output_file", output_file)
            return array

        file_commands = copy.deepcopy(terminal_commands.get(extension))
        if len(file_commands) == 1:
            execute_command = fill_fields_in_command(file_commands[-1])
        else:
            for command in file_commands[:-1]:
                command = fill_fields_in_command(command)
                compilation = subprocess.Popen(command, stderr=subprocess.PIPE)
                stderr = compilation.communicate()
                if stderr[1]:	# Check if the compilation causes an error
                    break
            else:				# Execute the program if there are no errors
                execute_command = fill_fields_in_command(file_commands[-1])
        # print(f"\n------ {self.file_name} ------")

        result = [self.file_name.split(".")[0]]
        if not execute_command:
            print("COMPILATION ERROR")
            return result + ["COMPILATION ERROR"] * len(self.test_input)


        # print("Executing: ", execute_command)
        test_number = 0
        correct_cases = 0
        for test_input, test_output in zip(self.test_input, self.test_output):
            execution = subprocess.Popen(execute_command, \
                                            stdin=subprocess.PIPE, \
                                            stdout=subprocess.PIPE, \
                                            stderr=subprocess.PIPE, shell=True)
            # print(string_from_test_case(test_input))
            stdout, stderr = execution.communicate(string_from_test_case(test_input))
            # stdout, stderr = execution.communicate()
            stdout = stdout.decode(FORMAT)
            stderr = stderr.decode(FORMAT)

            test_number += 1

            if stderr:
                # print(f"TEST CASE {test_number} ERROR", stderr)
                result.append("ERROR \n Output: " + stderr.replace(",", ".").replace("\n", ""))
                continue
            print(stdout, ":", test_output)
            if verify_output(stdout, test_output):
                # print(f"TEST CASE {test_number} CORRECT")
                result.append("CORRECT")
                correct_cases += 1
            else:
                # print(f"TEST CASE {test_number} INCORRECT")
                result.append("INCORRECT \nOutput: \n" + stdout)

        # print(f"{correct_cases}/{len(test_input)} CORRECT")
        return result

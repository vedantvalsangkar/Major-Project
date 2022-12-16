FORMAT = "utf-8"

# Helper Functions
def is_number(number):
    try:
        float(number)
        return True
    except ValueError:
        return False

def string_from_test_case(test_input):
    input_string = ""
    for digits in test_input:
        input_string += " ".join(map(str, digits))
        input_string += "\n"
    return input_string.encode(FORMAT)

def verify_output(stdout, program_output):
    digits = []
    for line in stdout.split("\n"):
        if not line:
            continue
        for number in line.split(" "):
            if is_number(number):
                digits.append(float(number))
            else:
                digits.append(number)
    if len(digits) != len(program_output):
        return False
    for digit, expected_digit in zip(digits, program_output):
        if digit != float(expected_digit):
            return False
    return True

def replace(array, elem, new_elem):
    try:
        index = array.index(elem)
    except ValueError:
        return array
    array[index] = new_elem
    return array
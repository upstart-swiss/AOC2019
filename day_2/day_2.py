

def intcode(opcodes: list):
    position = 0
    while position < len(opcodes):
        if opcodes[position] == 99:
            return opcodes
        elif opcodes[position] == 1:
            digit_1 = opcodes[opcodes[position + 1]]
            digit_2 = opcodes[opcodes[position + 2]]
            output = opcodes[position + 3]
            opcodes[output] = digit_1 + digit_2
            position = position + 4
            continue
        elif opcodes[position] == 2:
            digit_1 = opcodes[opcodes[position + 1]]
            digit_2 = opcodes[opcodes[position + 2]]
            output = opcodes[position + 3]
            opcodes[output] = digit_1 * digit_2
            position = position + 4
            continue
        else:
            print("Unknown opcode")
            position += 1
    pass

def test_intcode():
    assert intcode([1,0,0,0,99]) == [2,0,0,0,99]
    assert intcode([2,3,0,3,99]) == [2,3,0,6,99]
    assert intcode([2,4,4,5,99,0]) == [2,4,4,5,99,9801]
    assert intcode([1,1,1,4,99,5,6,0,99]) == [30,1,1,4,2,5,6,0,99]

def find_input(opcodes, desired_output):
    output = 0
    og_opcodes = opcodes.copy()
    a = 0
    counter=0
    while a <= 99:
        b = 0
        while b <= 99:
            counter += 1
            opcodes[1] = a
            opcodes[2] = b
            output = intcode(opcodes)[0]
            print(output)
            if output == desired_output:
                return a, b
            opcodes = og_opcodes.copy()
            b += 1
        a += 1
    print(counter)
    raise Exception("No Vals Found")


day_2_input = [1,0,0,3,1,1,2,3,1,3,4,3,1,5,0,3,2,9,1,19,1,5,19,23,2,9,23,27,1,27,5,31,2,31,13,35,1,35,9,39,1,39,10,43,2,43,9,47,1,47,5,51,2,13,51,55,1,9,55,59,1,5,59,63,2,6,63,67,1,5,67,71,1,6,71,75,2,9,75,79,1,79,13,83,1,83,13,87,1,87,5,91,1,6,91,95,2,95,13,99,2,13,99,103,1,5,103,107,1,107,10,111,1,111,13,115,1,10,115,119,1,9,119,123,2,6,123,127,1,5,127,131,2,6,131,135,1,135,2,139,1,139,9,0,99,2,14,0,0]
day_2_pt_1_input = day_2_input.copy()
day_2_pt_1_input[1] = 12
day_2_pt_1_input[2] = 3
if __name__ == "__main__":
    output_pt_1 = intcode(day_2_pt_1_input)
    print(f"Part 1: {output_pt_1[0]}")
    day_2_noun, day_2_verb = find_input(day_2_input, 19690720)
    day_2_answer = 100 * day_2_noun + day_2_verb
    print(f"Part 2: {day_2_answer}")
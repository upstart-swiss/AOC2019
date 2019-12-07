from abc import ABC, abstractmethod
from functools import lru_cache
import itertools

class OpCode(ABC):
    
    def __init__(self, opcodes, current_position, **kwargs):
        current_code = opcodes[current_position]
        if opcodes[current_position] % 100 != self.my_opcode:
            raise Exception("Bad Opcode")
        self.modes = False
        self.parse_modes(current_code)
        self._opcodes = opcodes
        self.should_continue = True
        self.position = current_position
        self.base_position = current_position
        self.kwargs = kwargs
        self.output = None
        self.ran = False
    
    @property
    @lru_cache()
    def opcodes(self):
        if self.ran:
            return self._opcodes
        self.operation()
        self.ran = True
        return self._opcodes
    
    def parse_modes(self, opcode):
        if opcode < 100:
            return
        opstring = str(opcode).zfill(5)
        self.modes = opstring[-3::-1]
        # print(f"Modes: {self.modes}")

    def fetch_value(self, position, mode="0"):
        # Modes are 0 - position 1 - immediate
        # print(f"Fetching {position} - {self._opcodes[position]}")
        if self.modes:
            mode = self.modes[position - self.base_position - 1]
        if mode == "0":
            return self._opcodes[self._opcodes[position]]
        elif mode == "1":
            return self._opcodes[position]
    
    @property
    def param_1(self):
        position = self.base_position + 1
        return self.fetch_value(position)
    
    @property
    def param_2(self):
        position = self.base_position + 2
        return self.fetch_value(position)

    @property
    def param_3(self):
        position = self.base_position + 3
        return self._opcodes[position]

    @property
    @abstractmethod
    def my_opcode(self):
        pass

    
    @abstractmethod
    def operation(self):
        pass

class OpCode1(OpCode):
    # Add Params
    @property
    def my_opcode(self):
        return 1

    def operation(self):
        # print(f"Param1 {self.param_1}, Param2 {self.param_2}, param3 {self.param_3} ")
        self._opcodes[self.param_3] = self.param_1 + self.param_2
        self.position += 4

class OpCode2(OpCode):
    # Multiply Params
    @property
    def my_opcode(self):
        return 2
            
    def operation(self):
        # print(f"Param1 {self.param_1}, Param2 {self.param_2}, param3 {self.param_3} ")
        self._opcodes[self.param_3] = self.param_1 * self.param_2
        self.position += 4
    
class OpCode99(OpCode):
    # Halt
    @property
    def my_opcode(self):
        return 99

    def operation(self):
        self.should_continue = False

class OpCode3(OpCode):
    # Input
    @property
    def my_opcode(self):
        return 3
    
    def operation(self):
        # Store a value provided to position
        this_input = int(self.kwargs["input"]) if "input" in self.kwargs else int(input("Program input: "))
        # print(f"putting {this_input} in position {self.param_1}")
        self.modes = "111"
        self._opcodes[self.param_1] = this_input
        self.position += 2

class OpCode4(OpCode):
    # Output (Print)
    @property
    def my_opcode(self):
        return 4
    
    def operation(self):
        digit = self.param_1
        #print(f"Output: {digit}")
        self.output = digit
        self.position += 2

class OpCode5(OpCode):
    # Jump if true
    @property
    def my_opcode(self):
        return 5
    
    def operation(self):
        if self.param_1 != 0:
            self.position = self.param_2
        else:
            self.position += 3

class OpCode6(OpCode):
    # Jump if false
    @property
    def my_opcode(self):
        return 6
    
    def operation(self):
        if self.param_1 == 0:
            self.position = self.param_2
        else:
            self.position += 3

class OpCode7(OpCode):
    # Less Than
    @property
    def my_opcode(self):
        return 7
    
    def operation(self):
        if self.param_1 < self.param_2:
            output = 1
        else:
            output = 0
        self._opcodes[self.param_3] = output
        self.position += 4

class OpCode8(OpCode):
    # Equals
    @property
    def my_opcode(self):
        return 8
    
    def operation(self):
        if self.param_1 == self.param_2:
            output = 1
        else:
            output = 0
        self._opcodes[self.param_3] = output
        self.position += 4
    
class OpCodeProcessor:
    opcode_runners = {
        1: OpCode1,
        2: OpCode2,
        3: OpCode3,
        4: OpCode4,
        5: OpCode5,
        6: OpCode6,
        7: OpCode7,
        8: OpCode8,
        99: OpCode99
    }
    def __init__(self, opcodes, runself=True, inputs=[], interactive=False, **kwargs):
        self.position = 0
        self.opcodes = opcodes.copy()
        self.kwargs = kwargs
        self.inputs = inputs
        self.complete = False
        self.interactive = interactive
        self.outputs = []
        if runself:
            self.run()
    
    def run(self):
        while self.position < len(self.opcodes):
            code = self.opcodes[self.position]
            if code % 100 not in self.opcode_runners:
                print(f"Position {self.position} with opcodes {self.opcodes}")
                raise Exception("Failed to run!")
            runner = self.opcode_runners[code % 100]
            # print(f"223 is {self._opcodes[223]}")
            # print(f"224 is {self._opcodes[224]}")
            # print(f"running pos {self.position} - code {code} - {self._opcodes[self.position:self.position + 4]}")
            if runner == OpCode3 and self.inputs != []:
                op = runner(self.opcodes, self.position, input=self.inputs.pop(0))
            elif runner == OpCode3 and self.interactive is False:
                return
            else:
                op = runner(self.opcodes, self.position)
            self.opcodes = op.opcodes
            self.position = op.position
            if op.output is not None:
                self.outputs.append(op.output)
            if op.should_continue is False:
                self.complete = True
                return

class Amplifier(OpCodeProcessor):
    def __init__(self, opcodes, phase, prev_output=None, **kwargs):
        inputs = [phase]
        if prev_output != None:
            inputs.append(prev_output)
        super().__init__(opcodes, inputs=inputs, **kwargs)
    


class AmplifierRunner:
    def __init__(self, opcodes):
        self.opcodes = opcodes
        self.phase_ouputs = []
        self.amps = []
    
    @property
    def output(self):
        return self.phase_ouputs[-1]
    
    def run_sequence(self, sequence):
        if len(sequence) != 5:
            raise Exception("Bad Seq")
        prev_output = 0
        for index, phase in enumerate(sequence):
            a = Amplifier(self.opcodes, phase, prev_output)
            if len(a.outputs) > 1:
                raise Exception("longer outputs")
            self.phase_ouputs.append(a.outputs[-1])
            prev_output = a.outputs[-1]
            self.amps.append(a)
    
    def run_feedback(self, sequence):
        self.run_sequence(sequence)
        self.continue_running()
    
    def continue_running(self):
        prev_output = self.phase_ouputs[-1]
        for amp in self.amps:
            if amp.complete is True:
                return
            amp.inputs.append(prev_output)
            amp.run()
            prev_output = amp.outputs[-1]
            self.phase_ouputs.append(prev_output)
        self.continue_running()



def test_day2():
    assert OpCodeProcessor([1,0,0,0,99]).opcodes == [2,0,0,0,99]
    assert OpCodeProcessor([2,3,0,3,99]).opcodes == [2,3,0,6,99]
    assert OpCodeProcessor([2,4,4,5,99,0]).opcodes == [2,4,4,5,99,9801]
    assert OpCodeProcessor([1,1,1,4,99,5,6,0,99]).opcodes == [30,1,1,4,2,5,6,0,99]

def test_day5():
    day_5_input = [3,225,1,225,6,6,1100,1,238,225,104,0,1101,48,82,225,102,59,84,224,1001,224,-944,224,4,224,102,8,223,223,101,6,224,224,1,223,224,223,1101,92,58,224,101,-150,224,224,4,224,102,8,223,223,1001,224,3,224,1,224,223,223,1102,10,89,224,101,-890,224,224,4,224,1002,223,8,223,1001,224,5,224,1,224,223,223,1101,29,16,225,101,23,110,224,1001,224,-95,224,4,224,102,8,223,223,1001,224,3,224,1,223,224,223,1102,75,72,225,1102,51,8,225,1102,26,16,225,1102,8,49,225,1001,122,64,224,1001,224,-113,224,4,224,102,8,223,223,1001,224,3,224,1,224,223,223,1102,55,72,225,1002,174,28,224,101,-896,224,224,4,224,1002,223,8,223,101,4,224,224,1,224,223,223,1102,57,32,225,2,113,117,224,101,-1326,224,224,4,224,102,8,223,223,101,5,224,224,1,223,224,223,1,148,13,224,101,-120,224,224,4,224,1002,223,8,223,101,7,224,224,1,223,224,223,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,8,677,226,224,102,2,223,223,1006,224,329,101,1,223,223,107,677,677,224,1002,223,2,223,1006,224,344,101,1,223,223,8,226,677,224,102,2,223,223,1006,224,359,101,1,223,223,107,226,226,224,102,2,223,223,1005,224,374,1001,223,1,223,1108,677,226,224,1002,223,2,223,1006,224,389,101,1,223,223,107,677,226,224,102,2,223,223,1006,224,404,1001,223,1,223,1107,226,677,224,1002,223,2,223,1006,224,419,1001,223,1,223,108,677,677,224,102,2,223,223,1005,224,434,1001,223,1,223,1008,677,226,224,1002,223,2,223,1006,224,449,1001,223,1,223,7,226,677,224,1002,223,2,223,1006,224,464,1001,223,1,223,1007,677,677,224,102,2,223,223,1005,224,479,1001,223,1,223,1007,226,226,224,1002,223,2,223,1005,224,494,1001,223,1,223,108,226,226,224,1002,223,2,223,1005,224,509,1001,223,1,223,1007,226,677,224,1002,223,2,223,1006,224,524,101,1,223,223,1107,677,677,224,102,2,223,223,1005,224,539,101,1,223,223,1107,677,226,224,102,2,223,223,1005,224,554,1001,223,1,223,108,677,226,224,1002,223,2,223,1006,224,569,1001,223,1,223,1108,226,677,224,1002,223,2,223,1006,224,584,101,1,223,223,8,677,677,224,1002,223,2,223,1006,224,599,1001,223,1,223,1008,226,226,224,102,2,223,223,1006,224,614,101,1,223,223,7,677,677,224,1002,223,2,223,1006,224,629,101,1,223,223,1008,677,677,224,102,2,223,223,1005,224,644,101,1,223,223,7,677,226,224,1002,223,2,223,1005,224,659,101,1,223,223,1108,226,226,224,102,2,223,223,1006,224,674,1001,223,1,223,4,223,99,226]
    assert OpCodeProcessor(day_5_input, inputs=["1"]).outputs[-1] == 13547311
    assert OpCodeProcessor(day_5_input, inputs=["5"]).outputs == [236453]


def test_day7():
    input_1 = [3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0]
    ar = AmplifierRunner(input_1)
    ar.run_sequence([4,3,2,1,0])
    assert ar.output == 43210
    input_2 = [3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0]
    ar = AmplifierRunner(input_2)
    ar.run_sequence([0,1,2,3,4])
    assert ar.output == 54321
    input_3 = [3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0]
    ar = AmplifierRunner(input_3)
    ar.run_sequence([1,0,4,3,2])
    assert ar.output == 65210

def test_day7_pt2():
    input_1 = [3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5]
    ar = AmplifierRunner(input_1)
    ar.run_feedback([9,8,7,6,5])
    assert ar.output == 139629729
    highest, combo = get_highest_signal(input_1, True)
    assert highest == 139629729
    assert combo == (9,8,7,6,5)
    input_2 = [3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10]
    ar = AmplifierRunner(input_2)
    ar.run_feedback([9,7,8,5,6])
    assert ar.output == 18216
    highest, combo = get_highest_signal(input_2, True)
    assert highest == 18216
    assert combo == (9,7,8,5,6)

def get_highest_signal(opcodes, feedback=False):
    highest = 0
    highest_combo = None
    combo_map = {}
    items = [0,1,2,3,4] if feedback is False else [5,6,7,8,9]
    for i in itertools.permutations(items):
        
        ar = AmplifierRunner(opcodes)
        if feedback is False:
            ar.run_sequence(i)
        if feedback is True:
            ar.run_feedback(i)
        combo_map[ar.output] = i
        if ar.output > highest:
            highest_combo = i
            highest = ar.output
    # print(combo_map)
    return highest, highest_combo

codes = [3,8,1001,8,10,8,105,1,0,0,21,34,51,64,73,98,179,260,341,422,99999,3,9,102,4,9,9,1001,9,4,9,4,9,99,3,9,1001,9,4,9,1002,9,3,9,1001,9,5,9,4,9,99,3,9,101,5,9,9,102,5,9,9,4,9,99,3,9,101,5,9,9,4,9,99,3,9,1002,9,5,9,1001,9,3,9,102,2,9,9,101,5,9,9,1002,9,2,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,101,1,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,101,1,9,9,4,9,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,101,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,1,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,99,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,102,2,9,9,4,9,3,9,102,2,9,9,4,9,3,9,101,2,9,9,4,9,3,9,1001,9,2,9,4,9,99,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,3,9,1001,9,1,9,4,9,3,9,101,1,9,9,4,9,3,9,102,2,9,9,4,9,3,9,1001,9,2,9,4,9,3,9,1002,9,2,9,4,9,3,9,1001,9,2,9,4,9,99]
if __name__ == "__main__":
    # op = OpCodeProcessor(day_5_input)
    # op.run()
    highest, combo = get_highest_signal(codes)
    print(f"HIghest combo is {highest} from {combo}")
    highest, combo = get_highest_signal(codes, True)
    print(f"HIghest feedback combo is {highest} from {combo}")



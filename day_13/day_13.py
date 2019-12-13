from abc import ABC, abstractmethod
from functools import lru_cache
import itertools
import warnings
import os 
import time 
class OpCode(ABC):
    takes_input = False
    
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
        self.relative_base = 0 
        if 'relative_base' in kwargs:
            self.relative_base = kwargs['relative_base']
    
    @property
    @lru_cache()
    def opcodes(self):
        if self.ran:
            return self._opcodes
        self.operation()
        self.ran = True
        return self._opcodes
    
    def run(self):
        if self.ran:
            return
        self.operation()
        self.ran = True
    
    def parse_modes(self, opcode):
        if opcode < 100:
            return
        opstring = str(opcode).zfill(5)
        self.modes = opstring[-3::-1]
        # print(f"Modes: {self.modes}")

    def fetch_value(self, position, write=False, mode="0"):
        # Modes are 0 - position 1 - immediate
        # Now 2 - Relative
        # print(f"Fetching {position} - {self._opcodes[position]}")
        data_at_loc = self._opcodes[position]
        if self.modes:
            mode = self.modes[position - self.base_position - 1]
        if mode == "1" and write:
            raise Exception("Cannot write in Immediate mode.")
        if mode == "0":
            position = data_at_loc
        elif mode == "1":
            position = position
        elif mode == "2":
            position = self.relative_base + data_at_loc
        else:
            raise Exception(f'Mode {mode} not known')
        if position >= len(self._opcodes):
            self._resize_to(position)
        if write:
            return position
        return self._opcodes[position]
    
    def set_value(self, position, data):
        if position >= len(self._opcodes):
            self._resize_to(position)
        self._opcodes[position] = data
        
    def _resize_to(self, size):
        extra_data = size - len(self._opcodes) + 1
        self._opcodes.extend([0 for i in range(extra_data)])
    
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
        return self.fetch_value(position)

    @property
    def write_param_1(self):
        position = self.base_position + 1
        return self.fetch_value(position, write=True)
    
    @property
    def write_param_2(self):
        position = self.base_position + 2
        return self.fetch_value(position, write=True)

    @property
    def write_param_3(self):
        position = self.base_position + 3
        return self.fetch_value(position, write=True)
    
    @property
    @abstractmethod
    def my_opcode(self):
        pass

    
    @abstractmethod
    def operation(self):
        pass
    
class OpCode99(OpCode):
    # Halt
    @property
    def my_opcode(self):
        return 99

    def operation(self):
        self.should_continue = False


class OpCode1(OpCode):
    # Add Params
    @property
    def my_opcode(self):
        return 1

    def operation(self):
        # print(f"Param1 {self.param_1}, Param2 {self.param_2}, param3 {self.param_3} ")
        self.set_value(self.write_param_3, self.param_1 + self.param_2)
        self.position += 4

class OpCode2(OpCode):
    # Multiply Params
    @property
    def my_opcode(self):
        return 2
            
    def operation(self):
        # print(f"Param1 {self.param_1}, Param2 {self.param_2}, param3 {self.param_3} ")
        self.set_value(self.write_param_3, self.param_1 * self.param_2)
        self.position += 4

class OpCode3(OpCode):
    takes_input = True
    # Input
    @property
    def my_opcode(self):
        return 3

    def operation(self):
        # Store a value provided to position
        this_input = int(self.kwargs["input"]) if "input" in self.kwargs else int(input("Program input: "))
        # print(f"Modes: {self.modes}")
        # print(f"putting {this_input} in position {self.write_param_1}")
        # print(f"Relative Base: {self.relative_base}")
        # print(f"{self._opcodes[self.position:self.position+2]}")
        self.set_value(self.write_param_1, this_input)
        # print(f"POsition {self.write_param_1}: {self._opcodes[self.write_param_1]}")
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
        self.set_value(self.write_param_3, output)
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
        self.set_value(self.write_param_3, output)
        self.position += 4
    
class OpCode9(OpCode):
    # Relative Base Modification
    @property
    def my_opcode(self):
        return 9
    
    def operation(self):
        self.relative_base += self.param_1
        self.position += 2

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
        9: OpCode9,
        99: OpCode99
    }
    def __init__(self, opcodes, inputs=[], interactive=False, **kwargs):
        self.position = 0
        self.opcodes = opcodes.copy()
        self.kwargs = kwargs
        self.inputs = inputs
        self.complete = False
        self.interactive = interactive
        self.outputs = []
        self.relative_base = 0
    
    def run(self):
        while self.position < len(self.opcodes):
            code = self.opcodes[self.position]
            if code % 100 not in self.opcode_runners:
                print(f"Position {self.position} with opcodes {self.opcodes}")
                raise Exception("Failed to run!")
            runner = self.opcode_runners[code % 100]
            # print(f"223 is {self._opcodes[223]}")
            # print(f"224 is {self._opcodes[224]}")
            #print(f"running pos {self.position} - code {code} - {self.opcodes[self.position:self.position + 4]}")
            if runner.takes_input and self.inputs != []:
                op = runner(self.opcodes, self.position, input=self.inputs.pop(0), relative_base=self.relative_base)
            elif runner.takes_input and self.interactive is False:
                # Pause until re-activated
                return
            else:
                op = runner(self.opcodes, self.position, relative_base=self.relative_base)
            op.run()
            self.opcodes = op.opcodes
            self.position = op.position
            if op.output is not None:
                self.outputs.append(op.output)
            self.relative_base = op.relative_base
            if op.should_continue is False:
                self.complete = True
                return

class ImmediateProcessor(OpCodeProcessor):
    def __init__(self, opcodes, **kwargs):
        super().__init__(opcodes, **kwargs)
        self.run()

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
            a.run()
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


def test_day2():
    assert ImmediateProcessor([1,0,0,0,99]).opcodes == [2,0,0,0,99]
    assert ImmediateProcessor([2,3,0,3,99]).opcodes == [2,3,0,6,99]
    assert ImmediateProcessor([2,4,4,5,99,0]).opcodes == [2,4,4,5,99,9801]
    assert ImmediateProcessor([1,1,1,4,99,5,6,0,99]).opcodes == [30,1,1,4,2,5,6,0,99]

def test_day5():
    day_5_input = [3,225,1,225,6,6,1100,1,238,225,104,0,1101,48,82,225,102,59,84,224,1001,224,-944,224,4,224,102,8,223,223,101,6,224,224,1,223,224,223,1101,92,58,224,101,-150,224,224,4,224,102,8,223,223,1001,224,3,224,1,224,223,223,1102,10,89,224,101,-890,224,224,4,224,1002,223,8,223,1001,224,5,224,1,224,223,223,1101,29,16,225,101,23,110,224,1001,224,-95,224,4,224,102,8,223,223,1001,224,3,224,1,223,224,223,1102,75,72,225,1102,51,8,225,1102,26,16,225,1102,8,49,225,1001,122,64,224,1001,224,-113,224,4,224,102,8,223,223,1001,224,3,224,1,224,223,223,1102,55,72,225,1002,174,28,224,101,-896,224,224,4,224,1002,223,8,223,101,4,224,224,1,224,223,223,1102,57,32,225,2,113,117,224,101,-1326,224,224,4,224,102,8,223,223,101,5,224,224,1,223,224,223,1,148,13,224,101,-120,224,224,4,224,1002,223,8,223,101,7,224,224,1,223,224,223,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,8,677,226,224,102,2,223,223,1006,224,329,101,1,223,223,107,677,677,224,1002,223,2,223,1006,224,344,101,1,223,223,8,226,677,224,102,2,223,223,1006,224,359,101,1,223,223,107,226,226,224,102,2,223,223,1005,224,374,1001,223,1,223,1108,677,226,224,1002,223,2,223,1006,224,389,101,1,223,223,107,677,226,224,102,2,223,223,1006,224,404,1001,223,1,223,1107,226,677,224,1002,223,2,223,1006,224,419,1001,223,1,223,108,677,677,224,102,2,223,223,1005,224,434,1001,223,1,223,1008,677,226,224,1002,223,2,223,1006,224,449,1001,223,1,223,7,226,677,224,1002,223,2,223,1006,224,464,1001,223,1,223,1007,677,677,224,102,2,223,223,1005,224,479,1001,223,1,223,1007,226,226,224,1002,223,2,223,1005,224,494,1001,223,1,223,108,226,226,224,1002,223,2,223,1005,224,509,1001,223,1,223,1007,226,677,224,1002,223,2,223,1006,224,524,101,1,223,223,1107,677,677,224,102,2,223,223,1005,224,539,101,1,223,223,1107,677,226,224,102,2,223,223,1005,224,554,1001,223,1,223,108,677,226,224,1002,223,2,223,1006,224,569,1001,223,1,223,1108,226,677,224,1002,223,2,223,1006,224,584,101,1,223,223,8,677,677,224,1002,223,2,223,1006,224,599,1001,223,1,223,1008,226,226,224,102,2,223,223,1006,224,614,101,1,223,223,7,677,677,224,1002,223,2,223,1006,224,629,101,1,223,223,1008,677,677,224,102,2,223,223,1005,224,644,101,1,223,223,7,677,226,224,1002,223,2,223,1005,224,659,101,1,223,223,1108,226,226,224,102,2,223,223,1006,224,674,1001,223,1,223,4,223,99,226]
    assert ImmediateProcessor(day_5_input, inputs=["1"]).outputs[-1] == 13547311
    assert ImmediateProcessor(day_5_input, inputs=["5"]).outputs == [236453]


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


def test_day9_pt1():
    input_1 = [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]
    runner_1 = ImmediateProcessor(input_1)
    assert runner_1.outputs == input_1
    input_2 = [1102,34915192,34915192,7,4,7,99,]
    assert len(str(ImmediateProcessor(input_2).outputs[0])) == 16
    assert ImmediateProcessor([104,1125899906842624,99]).outputs[0] == 1125899906842624
    # day_9_codes = [1102,34463338,34463338,63,1007,63,34463338,63,1005,63,53,1101,3,0,1000,109,988,209,12,9,1000,209,6,209,3,203,0,1008,1000,1,63,1005,63,65,1008,1000,2,63,1005,63,904,1008,1000,0,63,1005,63,58,4,25,104,0,99,4,0,104,0,99,4,17,104,0,99,0,0,1102,1,31,1008,1101,682,0,1027,1101,0,844,1029,1102,29,1,1001,1102,1,22,1014,1101,0,21,1011,1102,428,1,1025,1101,0,433,1024,1101,0,38,1019,1102,1,37,1016,1102,35,1,1017,1102,39,1,1018,1102,32,1,1000,1102,23,1,1012,1102,1,329,1022,1102,26,1,1006,1102,1,24,1003,1102,28,1,1005,1102,36,1,1010,1102,34,1,1004,1101,0,1,1021,1102,326,1,1023,1101,33,0,1015,1101,20,0,1002,1101,0,25,1007,1101,0,853,1028,1102,27,1,1009,1102,1,30,1013,1101,689,0,1026,1102,1,0,1020,109,12,2108,30,-3,63,1005,63,201,1001,64,1,64,1105,1,203,4,187,1002,64,2,64,109,-9,2101,0,6,63,1008,63,29,63,1005,63,227,1001,64,1,64,1106,0,229,4,209,1002,64,2,64,109,-6,1208,5,22,63,1005,63,249,1001,64,1,64,1106,0,251,4,235,1002,64,2,64,109,13,21107,40,41,8,1005,1018,273,4,257,1001,64,1,64,1105,1,273,1002,64,2,64,109,-11,2102,1,8,63,1008,63,25,63,1005,63,299,4,279,1001,64,1,64,1105,1,299,1002,64,2,64,109,15,1205,7,317,4,305,1001,64,1,64,1105,1,317,1002,64,2,64,109,10,2105,1,-1,1105,1,335,4,323,1001,64,1,64,1002,64,2,64,109,-22,1202,1,1,63,1008,63,24,63,1005,63,357,4,341,1106,0,361,1001,64,1,64,1002,64,2,64,109,13,1206,6,373,1106,0,379,4,367,1001,64,1,64,1002,64,2,64,109,11,1206,-6,393,4,385,1105,1,397,1001,64,1,64,1002,64,2,64,109,-32,1208,10,34,63,1005,63,419,4,403,1001,64,1,64,1105,1,419,1002,64,2,64,109,30,2105,1,0,4,425,1106,0,437,1001,64,1,64,1002,64,2,64,109,-28,1207,6,21,63,1005,63,455,4,443,1106,0,459,1001,64,1,64,1002,64,2,64,109,4,2101,0,8,63,1008,63,31,63,1005,63,485,4,465,1001,64,1,64,1105,1,485,1002,64,2,64,109,5,1207,-4,28,63,1005,63,505,1001,64,1,64,1106,0,507,4,491,1002,64,2,64,109,9,21102,41,1,2,1008,1016,39,63,1005,63,531,1001,64,1,64,1106,0,533,4,513,1002,64,2,64,109,-10,1201,4,0,63,1008,63,30,63,1005,63,553,1106,0,559,4,539,1001,64,1,64,1002,64,2,64,109,19,21108,42,41,-4,1005,1019,579,1001,64,1,64,1106,0,581,4,565,1002,64,2,64,109,-26,1201,3,0,63,1008,63,32,63,1005,63,607,4,587,1001,64,1,64,1106,0,607,1002,64,2,64,109,20,1205,3,623,1001,64,1,64,1105,1,625,4,613,1002,64,2,64,109,2,21107,43,42,-1,1005,1018,645,1001,64,1,64,1106,0,647,4,631,1002,64,2,64,109,-11,2102,1,1,63,1008,63,29,63,1005,63,667,1105,1,673,4,653,1001,64,1,64,1002,64,2,64,109,27,2106,0,-8,1001,64,1,64,1105,1,691,4,679,1002,64,2,64,109,-25,2107,25,-4,63,1005,63,713,4,697,1001,64,1,64,1105,1,713,1002,64,2,64,109,-2,21108,44,44,2,1005,1010,735,4,719,1001,64,1,64,1106,0,735,1002,64,2,64,109,11,21101,45,0,-3,1008,1016,45,63,1005,63,757,4,741,1106,0,761,1001,64,1,64,1002,64,2,64,109,-15,1202,3,1,63,1008,63,22,63,1005,63,781,1105,1,787,4,767,1001,64,1,64,1002,64,2,64,109,6,21101,46,0,0,1008,1010,49,63,1005,63,811,1001,64,1,64,1105,1,813,4,793,1002,64,2,64,109,-7,2108,34,1,63,1005,63,835,4,819,1001,64,1,64,1105,1,835,1002,64,2,64,109,15,2106,0,10,4,841,1001,64,1,64,1106,0,853,1002,64,2,64,109,-25,2107,33,7,63,1005,63,873,1001,64,1,64,1106,0,875,4,859,1002,64,2,64,109,7,21102,47,1,10,1008,1010,47,63,1005,63,897,4,881,1105,1,901,1001,64,1,64,4,64,99,21102,1,27,1,21102,915,1,0,1105,1,922,21201,1,12038,1,204,1,99,109,3,1207,-2,3,63,1005,63,964,21201,-2,-1,1,21102,942,1,0,1105,1,922,21202,1,1,-1,21201,-2,-3,1,21101,0,957,0,1106,0,922,22201,1,-1,-2,1106,0,968,22101,0,-2,-2,109,-3,2105,1,0]

class Direction:
    left = None
    right = None
    text = "None"
    def __repr__(self):
        return self.text

class UpDir(Direction):
    text = "^"
    movement = (0,1)

class LeftDir(Direction):
    right = UpDir
    text = "<"
    movement = (-1, 0)

class DownDir(Direction):
    right = LeftDir
    text = "v"
    movement = (0, -1)

class RightDir(Direction):
    left = UpDir
    right = DownDir
    text = ">"
    movement = (1, 0)

UpDir.left = LeftDir
UpDir.right = RightDir

LeftDir.left = DownDir

DownDir.left = RightDir

class Robot:
    directions = {
        "UP": UpDir,
        "LEFT": LeftDir,
        "RIGHT": RightDir,
        "DOWN": DownDir
    }
    def __init__(self, position=(0,0), opcodes=[], processor=OpCodeProcessor):
        self.direction = self.directions["UP"]
        self.processor = processor(opcodes)
        self.position = position

    def run(self):
        self.processor.run()

    def input_color(self, color_input):
        self.processor.inputs.append(color_input)
    
    @property
    def outputs(self):
        return self.processor.outputs
    
    def turn(self, direction):
        if direction == "left":
            self.direction = self.direction.left
        elif direction == "right":
            self.direction = self.direction.right
        self.position = (self.position[0] + self.direction.movement[0],
                         self.position[1] + self.direction.movement[1])

class Panel:
    colors = {
        "black": ".",
        "white": "#",
        ".": ".",
        "#": "#",
        0: ".",
        1: "#"
    }
    def __init__(self, color='.'):
        self.color = self.colors[color]
        self.painted_count = 0
    def assign(self, color):
        return self.paint(color)

    def paint(self, color):
        self.color = self.colors[color]
        self.painted_count += 1
    
    @property
    def painted(self):
        return True if self.painted_count > 0 else False
    
    @property
    def as_int(self):
        if self.color == ".":
            return 0
        elif self.color == "#":
            return 1
        else:
            raise Exception("unknown paint")
    
    def __repr__(self):
        return self.color
class Map:
    empty_type = None
    negatives = True
    def __init__(self, width=10, height=10):
        self.width=width
        self.height=height
        self.map_grid = {}
        self._initialize_map()
    
    def _initialize_map(self):
        height = self.height
        width = self.width
        neg_height = 0 - self.height if self.negatives else 0
        neg_width = 0 - self.width if self.negatives else 0
        for row in range(neg_height, 1+height):
            if row not in self.map_grid:
                self.map_grid[row] = {}
            for cell in range(neg_width, 1+width):
                if cell not in self.map_grid[row]:
                    self.map_grid[row][cell] = self.empty_type()
    
    def assign_grid_attribute(self, x, y, attribute):
        mapchange = False
        if y not in self.map_grid:
            self.height = abs(y)
            mapchange = True
        if x not in self.map_grid[0]:
            self.width = abs(x)
            mapchange = True
        if mapchange:
            self._initialize_map()
        self.map_grid[y][x].assign(attribute)
    @property
    def map(self):
        text = ""
        neg_height = 0 - self.height if self.negatives else 0
        neg_width = 0 - self.width if self.negatives else 0
        for row in range(self.height, neg_height-1, -1):
            for cell in range(neg_width, 1+self.width):
                text += str(self.map_grid[row][cell].as_str)
            text += "\n"
        return text
        
class Hull(Map):    
    @property
    def empty_type(self):
        return Panel
    def get_position_color(self, x, y):
        mapchange = False
        if y not in self.map_grid:
            self.height = abs(y)
            mapchange = True
        if x not in self.map_grid[0]:
            self.width = abs(x)
            mapchange = True
        if mapchange:
            self._initialize_map()
        return self.map_grid[y][x]
    
    @property
    def map(self):
        text = ""
        for row in range(self.height, 0-self.height-1, -1):
            for cell in range(0-self.width, 1+self.width):
                text += self.map_grid[row][cell].color
            text += "\n"
        return text
    
    def draw_robot_on_map(self, robot):
        text = ""
        x,y = robot.position
        for row in range(self.height, 0-self.height-1, -1):
            for cell in range(0-self.width, 1+self.width):
                if (cell, row) == (x, y):
                    text += robot.direction.text
                else:
                    text += self.map_grid[row][cell].color
            text += "\n"
        return text
    
    @property
    def painted_panel_count(self):
        paintcount = 0
        for row in self.map_grid:
            for cell in self.map_grid[row].values():
                if cell.painted:
                    paintcount += 1
        return paintcount


class RobotPainter:
    turn_dir = {
        0: "left",
        1: "right"
    }
    def __init__(self, opcodes=[]):
        self.hull = Hull()
        self.robot = Robot(opcodes=opcodes)
    
    @property
    def map(self):
        return self.hull.draw_robot_on_map(self.robot)
    
    def run_robot(self, debug=False):
        loops = 0
        while self.robot.processor.complete is False:
            loops +=1
            x, y = self.robot.position
            color = self.hull.get_position_color(x, y)
            if debug:
                print(f"sitting on {color} at coords {x}, {y}")
                print(f"loop {loops} - inputting {color.as_int} - robot facing {self.robot.direction}")
            self.robot.input_color(color.as_int)
            self.robot.run()
            while len(self.robot.outputs) > 0:
                x, y = self.robot.position
                color = self.robot.outputs.pop(0)
                direction = self.robot.outputs.pop(0)
                self.hull.assign_grid_attribute(x, y, color)
                self.robot.turn(self.turn_dir[direction])
                if debug:
                    print(f"Robot moved from {x,y} to {self.robot.position} when it turned {direction}")

class Ball:
    def __init__(self):
        pass
    def __repr__(self):
        return "x"
    
    def __str__(self):
        return "x"

class Tile:
    types = {
        0: " ",
        1: "|",
        2: Ball,
        3: "-",
        4: "."
    }
    def __init__(self, tile_type=0):
        self.type = self.types[tile_type]
        if self.type == Ball:
            self.type = Ball()
    
    def __repr__(self):
        return self.type

    @property
    def as_str(self):
        return self.type
    
    def assign(self, tile_type):
        self.type = self.types[tile_type]
        if self.type == Ball:
            self.type = Ball()


class Screen(Map):
    empty_type = Tile
    negatives = False

    def handle_output(x, y, tile):
        self.assign_grid_attribute(x, y, tile)


class GameScreen:
    def __init__(self, opcodes=[]):
        self.screen = Screen()
        self.runner = OpCodeProcessor(opcodes)
        self.score = 0
        self.ball_x = 0
        self.paddle_x = 0
    
    def run_runner(self):
        self.runner.run()
        while len(self.runner.outputs) > 0:
            x = self.runner.outputs.pop(0)
            y = self.runner.outputs.pop(0)
            tile_type = self.runner.outputs.pop(0)
            # This is far too specific, and it's bad i'm using it 
            if tile_type == 4:
                # print(f"ball at {x}")
                self.ball_x = x
            elif tile_type == 3:
                self.paddle_x = x
            if x == -1: # Score
                self.score = tile_type
                continue
            self.screen.assign_grid_attribute(x, y, tile_type)
            # print(f"assigning {tile_type} at {x},{y}")

    @property
    def map(self):
        os.system("clear")
        t = "\n".join(self.screen.map.split("\n")[::-1])
        t += f"\n Score {self.score}"
        return t

class Game(GameScreen):
    def run_game(self):
        while True:
            self.run_runner()
            print(self.map)
            move = input("Move:")
            if move == "<":
                self.runner.inputs.append(-1)
            elif move == ">":
                self.runner.inputs.append(1)
            elif move == ".":
                self.runner.inputs.append(0)
            else:
                print("BAD MOVE")
    
    def auto_game(self, pause_freq=-1, sleep=None):
        step = 1
        while self.runner.complete is False:
            self.run_runner()
            print(self.map)
            # print(f"Paddle {self.paddle_x} Ball {self.ball_x}")
            if self.paddle_x < self.ball_x:
                self.runner.inputs.append(1)
                # print("RIGHT")
            elif self.paddle_x > self.ball_x:
                self.runner.inputs.append(-1)
                # print("Left")
            elif self.paddle_x == self.ball_x:
                self.runner.inputs.append(0)
                # print("Stay")
            else:
                print("WTF yo")
            if pause_freq != -1 and step % pause_freq == 0:
                input("pause")
            step += 1
            if sleep:
                time.sleep(sleep)

#day_11_ops = [3,8,1005,8,291,1106,0,11,0,0,0,104,1,104,0,3,8,1002,8,-1,10,101,1,10,10,4,10,108,0,8,10,4,10,1002,8,1,28,1,1003,20,10,2,1103,19,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,0,10,4,10,1001,8,0,59,1,1004,3,10,3,8,102,-1,8,10,1001,10,1,10,4,10,108,0,8,10,4,10,1001,8,0,84,1006,0,3,1,1102,12,10,3,8,1002,8,-1,10,101,1,10,10,4,10,1008,8,1,10,4,10,101,0,8,114,3,8,1002,8,-1,10,101,1,10,10,4,10,108,1,8,10,4,10,101,0,8,135,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,0,10,4,10,102,1,8,158,2,9,9,10,2,2,10,10,3,8,1002,8,-1,10,1001,10,1,10,4,10,1008,8,1,10,4,10,101,0,8,188,1006,0,56,3,8,1002,8,-1,10,1001,10,1,10,4,10,108,1,8,10,4,10,1001,8,0,212,1006,0,76,2,1005,8,10,3,8,102,-1,8,10,1001,10,1,10,4,10,108,1,8,10,4,10,1001,8,0,241,3,8,102,-1,8,10,101,1,10,10,4,10,1008,8,0,10,4,10,1002,8,1,264,1006,0,95,1,1001,12,10,101,1,9,9,1007,9,933,10,1005,10,15,99,109,613,104,0,104,1,21102,838484206484,1,1,21102,1,308,0,1106,0,412,21102,1,937267929116,1,21101,0,319,0,1105,1,412,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,3,10,104,0,104,1,3,10,104,0,104,0,3,10,104,0,104,1,21102,206312598619,1,1,21102,366,1,0,1105,1,412,21101,179410332867,0,1,21102,377,1,0,1105,1,412,3,10,104,0,104,0,3,10,104,0,104,0,21101,0,709580595968,1,21102,1,400,0,1106,0,412,21102,868389384552,1,1,21101,411,0,0,1106,0,412,99,109,2,21202,-1,1,1,21102,1,40,2,21102,1,443,3,21101,0,433,0,1106,0,476,109,-2,2105,1,0,0,1,0,0,1,109,2,3,10,204,-1,1001,438,439,454,4,0,1001,438,1,438,108,4,438,10,1006,10,470,1102,0,1,438,109,-2,2106,0,0,0,109,4,1202,-1,1,475,1207,-3,0,10,1006,10,493,21102,0,1,-3,21202,-3,1,1,21201,-2,0,2,21101,0,1,3,21102,1,512,0,1106,0,517,109,-4,2105,1,0,109,5,1207,-3,1,10,1006,10,540,2207,-4,-2,10,1006,10,540,22101,0,-4,-4,1106,0,608,21201,-4,0,1,21201,-3,-1,2,21202,-2,2,3,21101,0,559,0,1106,0,517,21201,1,0,-4,21102,1,1,-1,2207,-4,-2,10,1006,10,578,21101,0,0,-1,22202,-2,-1,-2,2107,0,-3,10,1006,10,600,21201,-1,0,1,21102,600,1,0,106,0,475,21202,-2,-1,-2,22201,-4,-2,-4,109,-5,2106,0,0]
day_13_ops = [1,380,379,385,1008,2235,224642,381,1005,381,12,99,109,2236,1102,1,0,383,1101,0,0,382,20101,0,382,1,20102,1,383,2,21101,37,0,0,1106,0,578,4,382,4,383,204,1,1001,382,1,382,1007,382,38,381,1005,381,22,1001,383,1,383,1007,383,21,381,1005,381,18,1006,385,69,99,104,-1,104,0,4,386,3,384,1007,384,0,381,1005,381,94,107,0,384,381,1005,381,108,1105,1,161,107,1,392,381,1006,381,161,1102,-1,1,384,1106,0,119,1007,392,36,381,1006,381,161,1102,1,1,384,21001,392,0,1,21102,1,19,2,21102,1,0,3,21102,138,1,0,1105,1,549,1,392,384,392,20101,0,392,1,21102,19,1,2,21102,3,1,3,21101,0,161,0,1105,1,549,1101,0,0,384,20001,388,390,1,21001,389,0,2,21102,1,180,0,1106,0,578,1206,1,213,1208,1,2,381,1006,381,205,20001,388,390,1,20101,0,389,2,21102,1,205,0,1105,1,393,1002,390,-1,390,1101,1,0,384,20101,0,388,1,20001,389,391,2,21101,228,0,0,1105,1,578,1206,1,261,1208,1,2,381,1006,381,253,21001,388,0,1,20001,389,391,2,21102,1,253,0,1105,1,393,1002,391,-1,391,1102,1,1,384,1005,384,161,20001,388,390,1,20001,389,391,2,21101,0,279,0,1105,1,578,1206,1,316,1208,1,2,381,1006,381,304,20001,388,390,1,20001,389,391,2,21102,304,1,0,1105,1,393,1002,390,-1,390,1002,391,-1,391,1102,1,1,384,1005,384,161,20101,0,388,1,21001,389,0,2,21102,1,0,3,21101,338,0,0,1106,0,549,1,388,390,388,1,389,391,389,20101,0,388,1,21002,389,1,2,21101,4,0,3,21102,1,365,0,1105,1,549,1007,389,20,381,1005,381,75,104,-1,104,0,104,0,99,0,1,0,0,0,0,0,0,228,17,16,1,1,19,109,3,21201,-2,0,1,21202,-1,1,2,21102,1,0,3,21102,414,1,0,1106,0,549,22101,0,-2,1,22102,1,-1,2,21102,429,1,0,1106,0,601,2102,1,1,435,1,386,0,386,104,-1,104,0,4,386,1001,387,-1,387,1005,387,451,99,109,-3,2105,1,0,109,8,22202,-7,-6,-3,22201,-3,-5,-3,21202,-4,64,-2,2207,-3,-2,381,1005,381,492,21202,-2,-1,-1,22201,-3,-1,-3,2207,-3,-2,381,1006,381,481,21202,-4,8,-2,2207,-3,-2,381,1005,381,518,21202,-2,-1,-1,22201,-3,-1,-3,2207,-3,-2,381,1006,381,507,2207,-3,-4,381,1005,381,540,21202,-4,-1,-1,22201,-3,-1,-3,2207,-3,-4,381,1006,381,529,22102,1,-3,-7,109,-8,2105,1,0,109,4,1202,-2,38,566,201,-3,566,566,101,639,566,566,1202,-1,1,0,204,-3,204,-2,204,-1,109,-4,2106,0,0,109,3,1202,-1,38,594,201,-2,594,594,101,639,594,594,20101,0,0,-2,109,-3,2106,0,0,109,3,22102,21,-2,1,22201,1,-1,1,21101,401,0,2,21102,392,1,3,21101,0,798,4,21102,630,1,0,1106,0,456,21201,1,1437,-2,109,-3,2106,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,2,0,2,0,0,0,0,0,2,2,0,2,0,2,2,0,2,2,0,0,2,0,2,0,2,2,2,2,2,0,2,0,2,0,0,1,1,0,2,2,0,0,2,0,0,2,2,0,2,2,0,2,2,0,2,0,0,0,2,2,2,2,0,2,2,2,2,0,2,0,0,2,0,1,1,0,0,2,2,2,2,0,2,2,0,2,2,0,2,2,0,0,2,2,0,2,2,2,2,2,2,0,2,2,0,2,0,0,2,0,0,1,1,0,0,0,2,2,2,2,2,2,2,2,2,2,0,0,0,2,2,0,0,2,2,0,2,2,2,2,0,2,2,0,2,2,0,2,0,1,1,0,0,2,2,0,0,2,2,0,0,0,2,2,2,0,2,0,2,0,2,2,2,0,0,0,2,0,0,2,0,0,2,0,2,0,0,1,1,0,2,0,0,2,2,0,0,0,2,0,2,2,0,2,0,0,2,0,2,2,2,2,0,2,2,2,2,2,0,0,0,0,2,0,0,1,1,0,0,2,0,0,0,2,0,0,0,0,2,2,2,2,0,0,2,0,0,0,2,2,0,2,0,0,2,2,0,0,2,2,0,2,0,1,1,0,2,0,2,0,0,0,0,2,0,0,0,0,2,2,0,2,2,2,0,0,2,2,0,0,2,2,0,0,0,0,0,0,0,0,0,1,1,0,0,2,0,2,2,0,0,0,2,0,2,2,0,2,0,2,2,2,0,2,0,0,0,2,2,0,0,2,0,2,0,2,2,0,0,1,1,0,2,2,2,0,0,0,2,2,0,0,0,2,0,2,2,0,2,2,2,2,2,0,2,0,2,2,2,0,2,2,0,0,0,2,0,1,1,0,2,2,0,0,2,0,0,2,0,2,0,2,0,2,0,0,0,0,0,2,0,2,2,0,2,2,0,0,0,2,0,0,0,0,0,1,1,0,2,2,2,0,2,2,0,0,0,2,2,0,2,2,0,2,2,0,0,2,0,0,0,2,2,2,2,0,0,2,2,2,2,0,0,1,1,0,0,0,2,0,0,0,2,2,0,2,2,0,0,2,0,2,2,0,2,0,0,2,0,2,0,0,0,0,2,0,0,2,2,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,4,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,10,48,35,61,53,72,4,25,78,80,93,75,28,59,84,96,49,34,7,5,7,83,51,20,10,57,32,48,82,60,1,84,51,32,75,9,22,31,59,1,27,36,88,91,69,90,73,31,68,45,25,14,69,27,35,5,49,65,59,21,82,69,24,98,14,40,38,51,36,21,95,83,59,93,98,16,29,25,63,21,11,9,65,12,26,56,61,55,65,57,77,56,75,91,75,70,9,72,61,74,64,70,37,14,48,50,27,66,84,49,10,69,1,28,64,69,41,50,17,61,53,37,29,50,75,46,44,9,5,54,41,24,25,68,68,71,69,44,36,40,85,18,75,62,3,93,13,26,20,31,20,19,31,3,82,24,57,20,61,75,53,2,35,41,8,64,60,2,69,4,82,8,63,40,6,77,58,61,57,33,4,51,44,26,19,77,67,82,80,21,3,85,29,17,47,56,44,23,16,71,25,74,25,9,34,14,84,65,80,72,75,11,90,11,68,50,85,90,31,75,21,45,43,20,16,47,22,42,75,87,32,97,4,91,68,42,54,63,6,64,3,87,33,47,88,67,88,68,5,8,42,30,1,93,34,89,74,12,24,95,24,45,52,10,40,7,71,36,82,61,52,7,64,45,58,10,48,40,49,16,10,1,34,98,87,66,88,71,64,81,93,34,68,66,47,42,82,52,7,54,60,53,64,54,97,36,88,62,81,9,77,98,63,16,16,66,96,29,88,78,77,10,6,80,2,78,55,98,59,51,49,86,33,2,55,35,6,94,62,98,53,64,29,59,63,58,38,70,81,34,65,65,58,89,47,8,87,10,65,88,85,53,51,19,54,45,83,81,72,34,67,39,73,70,73,86,47,18,70,61,50,22,91,67,71,17,17,54,57,83,24,48,66,87,16,70,13,9,4,15,86,58,78,52,11,22,89,19,20,94,26,96,33,53,12,22,44,91,10,24,14,78,6,4,3,66,66,68,61,18,58,88,14,61,26,90,55,23,40,77,94,15,51,42,12,40,79,28,91,66,28,43,66,61,77,37,53,52,12,86,35,25,74,16,84,72,94,70,69,27,42,41,82,22,59,26,29,76,97,34,6,38,32,32,42,66,29,50,85,94,8,47,11,24,80,19,29,6,40,11,84,1,62,27,93,4,78,64,87,85,62,70,43,33,33,22,39,93,75,46,25,1,94,95,75,20,51,96,16,47,65,24,7,95,3,54,90,86,30,76,88,43,52,57,39,43,92,8,69,22,43,67,94,76,64,85,50,88,58,6,6,60,3,35,24,66,44,15,12,93,82,21,4,27,55,59,34,2,63,38,93,70,82,77,28,77,55,24,67,31,81,43,86,9,92,49,85,48,83,41,4,66,36,44,19,14,67,65,41,8,96,66,86,74,93,49,26,38,16,66,71,12,93,59,85,23,56,5,55,80,60,91,11,79,11,39,39,37,42,16,43,48,12,31,18,28,39,14,21,63,64,85,39,37,40,87,40,60,82,79,78,59,66,63,4,25,76,13,63,43,68,10,35,65,84,10,25,16,81,87,57,37,36,18,49,21,72,63,83,39,19,51,30,35,96,4,64,10,46,38,62,27,2,52,65,75,6,6,13,69,88,64,89,28,6,73,67,17,10,1,92,27,98,10,94,94,70,95,71,13,77,45,53,54,73,41,23,29,29,33,23,70,63,46,85,45,14,89,92,45,18,36,64,46,51,78,39,3,31,37,31,12,12,59,10,68,65,92,85,70,83,5,34,17,16,60,62,51,44,28,1,32,61,52,40,7,97,1,51,79,9,13,42,15,14,92,77,18,224642]
if __name__ == "__main__":
    r0 = GameScreen(day_13_ops)
    r0.run_runner()

    # Let's play a game
    day_13_game = day_13_ops.copy()
    day_13_game[0] = 2
    r1 = Game(day_13_game)
    r1.auto_game(sleep=0.015)
    # print(f"Part 1 Painted Panels: {r0.hull.painted_panel_count}")
    # r = RobotPainter(day_11_ops)
    # r.hull.map_grid[0][0]
    # r.run_robot()
    # print("Part 2:")
    # print(r.map.replace(".", " ")) #more readable this way

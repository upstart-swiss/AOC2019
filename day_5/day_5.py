from abc import ABC, abstractmethod
from functools import lru_cache

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
        this_input = int(input("Program input: ")) #self.kwargs["input"] if "input" in self.kwargs else 1
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
        print(f"Output: {digit}")
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
    def __init__(self, opcodes, runself=True):
        self.position = 0
        self.opcodes = opcodes
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
            op = runner(self.opcodes, self.position)
            self.opcodes = op.opcodes
            self.position = op.position
            if op.should_continue is False:
                return


def test_day2():
    assert OpCodeProcessor([1,0,0,0,99]).opcodes == [2,0,0,0,99]
    assert OpCodeProcessor([2,3,0,3,99]).opcodes == [2,3,0,6,99]
    assert OpCodeProcessor([2,4,4,5,99,0]).opcodes == [2,4,4,5,99,9801]
    assert OpCodeProcessor([1,1,1,4,99,5,6,0,99]).opcodes == [30,1,1,4,2,5,6,0,99]


day_5_input = [3,225,1,225,6,6,1100,1,238,225,104,0,1101,48,82,225,102,59,84,224,1001,224,-944,224,4,224,102,8,223,223,101,6,224,224,1,223,224,223,1101,92,58,224,101,-150,224,224,4,224,102,8,223,223,1001,224,3,224,1,224,223,223,1102,10,89,224,101,-890,224,224,4,224,1002,223,8,223,1001,224,5,224,1,224,223,223,1101,29,16,225,101,23,110,224,1001,224,-95,224,4,224,102,8,223,223,1001,224,3,224,1,223,224,223,1102,75,72,225,1102,51,8,225,1102,26,16,225,1102,8,49,225,1001,122,64,224,1001,224,-113,224,4,224,102,8,223,223,1001,224,3,224,1,224,223,223,1102,55,72,225,1002,174,28,224,101,-896,224,224,4,224,1002,223,8,223,101,4,224,224,1,224,223,223,1102,57,32,225,2,113,117,224,101,-1326,224,224,4,224,102,8,223,223,101,5,224,224,1,223,224,223,1,148,13,224,101,-120,224,224,4,224,1002,223,8,223,101,7,224,224,1,223,224,223,4,223,99,0,0,0,677,0,0,0,0,0,0,0,0,0,0,0,1105,0,99999,1105,227,247,1105,1,99999,1005,227,99999,1005,0,256,1105,1,99999,1106,227,99999,1106,0,265,1105,1,99999,1006,0,99999,1006,227,274,1105,1,99999,1105,1,280,1105,1,99999,1,225,225,225,1101,294,0,0,105,1,0,1105,1,99999,1106,0,300,1105,1,99999,1,225,225,225,1101,314,0,0,106,0,0,1105,1,99999,8,677,226,224,102,2,223,223,1006,224,329,101,1,223,223,107,677,677,224,1002,223,2,223,1006,224,344,101,1,223,223,8,226,677,224,102,2,223,223,1006,224,359,101,1,223,223,107,226,226,224,102,2,223,223,1005,224,374,1001,223,1,223,1108,677,226,224,1002,223,2,223,1006,224,389,101,1,223,223,107,677,226,224,102,2,223,223,1006,224,404,1001,223,1,223,1107,226,677,224,1002,223,2,223,1006,224,419,1001,223,1,223,108,677,677,224,102,2,223,223,1005,224,434,1001,223,1,223,1008,677,226,224,1002,223,2,223,1006,224,449,1001,223,1,223,7,226,677,224,1002,223,2,223,1006,224,464,1001,223,1,223,1007,677,677,224,102,2,223,223,1005,224,479,1001,223,1,223,1007,226,226,224,1002,223,2,223,1005,224,494,1001,223,1,223,108,226,226,224,1002,223,2,223,1005,224,509,1001,223,1,223,1007,226,677,224,1002,223,2,223,1006,224,524,101,1,223,223,1107,677,677,224,102,2,223,223,1005,224,539,101,1,223,223,1107,677,226,224,102,2,223,223,1005,224,554,1001,223,1,223,108,677,226,224,1002,223,2,223,1006,224,569,1001,223,1,223,1108,226,677,224,1002,223,2,223,1006,224,584,101,1,223,223,8,677,677,224,1002,223,2,223,1006,224,599,1001,223,1,223,1008,226,226,224,102,2,223,223,1006,224,614,101,1,223,223,7,677,677,224,1002,223,2,223,1006,224,629,101,1,223,223,1008,677,677,224,102,2,223,223,1005,224,644,101,1,223,223,7,677,226,224,1002,223,2,223,1005,224,659,101,1,223,223,1108,226,226,224,102,2,223,223,1006,224,674,1001,223,1,223,4,223,99,226]
if __name__ == "__main__":
    op = OpCodeProcessor(day_5_input)
    op.run()

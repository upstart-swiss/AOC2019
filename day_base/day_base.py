from abc import ABC, abstractmethod

class Day_Base:
    def __init__(self, my_input):
        self.compute_answer()
        pass
    
    @property
    def answer(self):
        # Replace with the real variable
        return None

    @abstractmethod
    def compute_answer(self):
        pass

class Day_Pt1(Day_Base):
    def compute_answer(self):
        pass

class Day_Pt2(Day_Base):
    def compute_answer(self):
        pass


def test_pt1():
    input1 = ""
    answer1 = None

    input2 = ""
    answer2 = None

    input3 = ""
    answer3 = None
    assert Day_Pt1(input1) == answer1
    assert Day_Pt1(input2) == answer2
    assert Day_Pt1(input3) == answer3

def test_pt2():
    input1 = ""
    answer1 = None

    input2 = ""
    answer2 = None

    input3 = ""
    answer3 = None
    assert Day_Pt2(input1) == answer1
    assert Day_Pt2(input2) == answer2
    assert Day_Pt2(input3) == answer3



from abc import ABC, abstractmethod

class Day5_Base:
    def __init__(self):
        self.compute_answer()
        pass
    
    @property
    def answer(self):
        # Replace with the real variable
        return None

    @abstractmethod
    def compute_answer(self):
        pass

class Day5_Pt1(Day5_Base):
    def compute_answer(self):
        pass

class Day5_Pt2(Day5_Base):
    def compute_answer(self):
        pass


def test_pt1():
    input1 = ""
    answer1 = ""

    input2 = ""
    answer2 = ""

    input3 = ""
    answer3 = ""
    assert Day5_Pt1(input1) == answer1
    assert Day5_Pt1(input2) == answer2
    assert Day5_Pt1(input3) == answer3

def test_pt2():
    input1 = ""
    answer1 = ""

    input2 = ""
    answer2 = ""

    input3 = ""
    answer3 = ""
    assert Day5_Pt2(input1) == answer1
    assert Day5_Pt2(input2) == answer2
    assert Day5_Pt2(input3) == answer3



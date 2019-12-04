import math

## Trying my new method that I'll try for Day 5
from abc import ABC, abstractmethod

class Day1_Base:
    def __init__(self, mass):
        mass = float(mass)
        self.mass = mass
        self.fuel = None
        self.compute_answer()
        pass

    def compute_fuel_for_mass(self, mass):
        divided = mass/3.00
        floored = math.floor(divided)
        fuel = floored - 2
        if fuel < 0:
            fuel = 0
        return fuel

    @property
    def answer(self):
        return self.fuel

    @abstractmethod
    def compute_answer(self):
        pass

class Day1_Pt1(Day1_Base):
    def compute_answer(self):
        self.fuel = self.compute_fuel_for_mass(self.mass)


class Day1_Pt2(Day1_Base):
    def compute_answer(self):
        mass_left = self.mass
        current_fuel = 0
        while mass_left > 0:
            fuel = self.compute_fuel_for_mass(mass_left)
            current_fuel += fuel
            mass_left = fuel
        self.fuel = current_fuel


def test_pt1():
    input1 = 12
    answer1 = 2

    input2 = 14
    answer2 = 2

    input3 = 1969
    answer3 = 654

    input4 = 100756
    answer4 = 33583

    assert Day1_Pt1(input1).answer == answer1
    assert Day1_Pt1(input2).answer == answer2
    assert Day1_Pt1(input3).answer == answer3
    assert Day1_Pt1(input4).answer == answer4

def test_pt2():
    input1 = 14
    answer1 = 2

    input2 = 1969
    answer2 = 966

    input3 = 100756
    answer3 = 50346
    assert Day1_Pt2(input1).answer == answer1
    assert Day1_Pt2(input2).answer == answer2
    assert Day1_Pt2(input3).answer == answer3


## Original Method Below
def calc_fuel_req(mass):
    mass = float(mass)
    divided_mass = mass/3.0
    floored_math = math.floor(divided_mass)
    fuel = floored_math - 2
    if fuel < 0:
        fuel = 0
    return fuel

def calc_recursive_fuel(mass):
    fuel = calc_fuel_req(mass)
    if fuel == 0:
        return fuel
    additional_fuel = calc_recursive_fuel(fuel)
    return fuel + additional_fuel

def test_fuel():
    assert calc_fuel_req(12) == 2
    assert calc_fuel_req(14) == 2
    assert calc_fuel_req(1969) == 654
    assert calc_fuel_req(100756) == 33583

def test_recursive_fuel():
    assert calc_recursive_fuel(14) == 2
    assert calc_recursive_fuel(1969) == 966
    assert calc_recursive_fuel(100756) == 50346

if __name__ == "__main__":
    comp_input = open("day_1_input.txt")
    total = 0
    pt_2_total = 0
    for line in comp_input:
        total += Day1_Pt1(line).answer
        pt_2_total += Day1_Pt2(line).answer
    print(f"Part 1 fuel requirements is: {total}")
    print(f"Part 2 fuel requirements is: {pt_2_total}")

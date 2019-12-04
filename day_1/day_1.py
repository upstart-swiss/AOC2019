import math


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
        total += calc_fuel_req(line)
        pt_2_total += calc_recursive_fuel(line)
    print(f"Part 1 fuel requirements is: {total}")
    print(f"Part 2 fuel requirements is: {pt_2_total}")

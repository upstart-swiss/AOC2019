from abc import ABC, abstractmethod

class Moon:
    def __init__(self, position=[0,0,0], velocity=[0,0,0]):
        self.compute_answer()
        self.velocity = velocity.copy()
        self.position = position
        self.original_position = position
        self.time = 0
    
    @property
    def answer(self):
        # Replace with the real variable
        return None

    def advance(self):
        self.time += 1
        self.position = (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1],
            self.position[2] + self.velocity[2]
        )

    @abstractmethod
    def compute_answer(self):
        pass
    def apply_gravity(self, other_moon):
        for index, value in enumerate(other_moon.position):
            if  value > self.position[index]:
                self.velocity[index] += 1
            elif value < self.position[index]:
                self.velocity[index] -= 1
            else:
                continue
    
    def __repr__(self):
        return f"<Moon pos<x={self.position[0]} y={self.position[1]} z={self.position[2]}> vel<x={self.velocity[0]} y={self.velocity[1]} z={self.velocity[2]}>>"
    @property
    def kinetic_energy(self):
        energy = 0
        for i in self.velocity:
            energy += abs(i)
        return energy
        
    @property
    def potential_energy(self):
        energy = 0
        for i in self.position:
            energy += abs(i)
        return energy
    
    @property
    def total_energy(self):
        return self.potential_energy * self.kinetic_energy
    
class Moon2(Moon):
    @property
    def in_original(self):
        if self.original_position == self.position:
            return True
        return False

class System:
    def __init__(self, moons=[]):
        self.moons = moons.copy()
        self.test_moons = []
        self.time = 0
    
    def add_moon(self, moon):
        self.moons.append(moon)
    
    def time_step(self, steps=1):
        for step in range(steps):
            self.apply_gravities()
            for moon in self.moons:
                moon.advance()
            self.time += 1
    
    def apply_gravities(self):
        for index in range(len(self.moons)):
            for other in range(len(self.moons)):
                if index == other:
                    continue
                self.moons[index].apply_gravity(self.moons[other])
    
    @property
    def total_energy(self):
        energy = 0
        for moon in self.moons:
            energy += moon.total_energy
        return energy

class System2(System):
    @property
    def in_original(self):
        for moon in self.moons:
            if moon.in_original is False:
                return False
        return True

    def loop_to_original(self, limit=-1):
        while not self.in_original:
            if limit != -1:
                if self.time > limit:
                    return False
            if self.time % 10000 == 0:
                print(self.time)
            self.time_step()
        print(f"Original at time: {self.time}")

class Day_Pt1(Moon):
    def compute_answer(self):
        pass

class Day_Pt2(Moon):
    def compute_answer(self):
        pass


def test_pt1():
    moons_1 = [Moon((-1,0,2)), Moon((2,-10,-7)), Moon((4,-8,8)), Moon((3,5,-1))]
    system_1 = System(moons=moons_1)
    system_1.time_step()
    # answer1 = None

    # input2 = ""
    # answer2 = None

    # input3 = ""
    # answer3 = None
    # assert Day_Pt1(input1) == answer1
    # assert Day_Pt1(input2) == answer2
    # assert Day_Pt1(input3) == answer3

def test_pt2():
    moons_2 = [
        Moon2((-1,0,2)),
        Moon2((2,-10,-7)), 
        Moon2((4,-8,8)), 
        Moon2((3,5,-1))]
    system_2 = System2(moons=moons_2)
    system_2.time_step()
    system_2.loop_to_original(limit=2772)
    assert system_2.time == 2772
    answer1 = None

    input2 = ""
    answer2 = None

    input3 = ""
    answer3 = None
    assert Day_Pt2(input1) == answer1
    assert Day_Pt2(input2) == answer2
    assert Day_Pt2(input3) == answer3


if __name__ == "__main__":
    moons_1 = [
        Moon2((3,2,-6)), 
        Moon2((-13,18,10)), 
        Moon2((-8, -1, 13)), 
        Moon2((5,10,4))]
    system_1 = System2(moons=moons_1)
    system_1.time_step(1000)
    print(f"Energy: {system_1.total_energy}")
    system_1.loop_to_original()
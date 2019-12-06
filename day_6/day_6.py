from functools import lru_cache
from abc import ABC, abstractmethod

class SolarSystem:
    def __init__(self):
        self.planets = {}
    
    @property
    def total_orbits(self):
        orbits = 0
        for planet in self.planets:
            orbits += self.total_orbits_for_planet(planet)
        return orbits

    def get_planet(self, planet_name):
        if planet_name not in self.planets:
            raise Exception("Planet not in system")
        planet = self.planets[planet_name]
        return planet

    def direct_orbits_for_planet(self, planet_name):
        planet = self.get_planet(planet_name)
        return len(planet.parents)
    
    def indirect_orbits_for_planet(self, planet_name):
        orbits = 0
        planet = self.get_planet(planet_name)
        parents = planet.parents
        for parent in parents:
            orbits += self.total_orbits_for_planet(parent.name)
        return orbits

    def total_orbits_for_planet(self, planet_name):
        return self.direct_orbits_for_planet(planet_name) + self.indirect_orbits_for_planet(planet_name)
    
    def add_orbit(self, parent, child):
        parent_planet = None
        child_planet = None
        if parent in self.planets:
            parent_planet = self.planets[parent]
        else:
            parent_planet = Planet(parent)
        if child in self.planets:
            child_planet = self.planets[child]
        else:
            child_planet = Planet(child)
        parent_planet.children.append(child_planet)
        child_planet.add_parent(parent_planet)
        self.planets[parent] = parent_planet
        self.planets[child] = child_planet
    
class Transfer:
    def __init__(self, start_planet, end_planet):
        self.visited = {}
        self.start = start_planet
        self.end = end_planet
        self.end_parents = []
        self.start_parents = []
        self.path = []
        self.distance = -1
    
    @staticmethod
    def get_all_parents(planet):
        parents = [planet]
        current_planet = planet
        while len(current_planet.parents) != 0:
            parent = current_planet.parents[0]
            parents.append(parent)
            current_planet = parent
        return parents
    
    @staticmethod
    def find_common_parent(list1, list2):
        for item in list1:
            if item in list2:
                return item

    def run(self):
        self.start_parents = self.get_all_parents(self.start)
        self.end_parents = self.get_all_parents(self.end)
        common_parent = self.find_common_parent(self.start_parents, self.end_parents)
        start_path = self.start_parents[:self.start_parents.index(common_parent)+1]
        end_path = self.end_parents[:self.end_parents.index(common_parent)]
        self.path = start_path
        self.path.extend(end_path[::-1])
        self.distance = len(self.path)
    
    @property
    def text_path(self):
        return [i.name for i in self.path]
    
    @property
    def required_transfers(self):
        return self.distance - 3
    

class Planet:
    #magic solar system
    def __init__(self, name):
        self.children = []
        self.end_stars = []
        self.parents = []
        self.name = name
        
    def add_parent(self, parent_planet):
        self.parents.append(parent_planet)
  
    @property
    @lru_cache()
    def answer(self):
        # Replace with the real variable
        self.compute_answer()
        return self._answer()
    
    def __repr__(self):
        return f"<Planet {self.name}>"

class Planet_pt1(Planet):
    def compute_answer(self):
        pass

def test_pt1():
    test_map = """
    COM)B
    B)C
    C)D
    D)E
    E)F
    B)G
    G)H
    D)I
    E)J
    J)K
    K)L
    """
    system = create_system_from_map(test_map)
    assert system.total_orbits_for_planet("D") == 3
    assert system.total_orbits_for_planet("L") == 7
    assert system.total_orbits_for_planet("COM") == 0

def test_pt2():
    test_map = """
    COM)B
    B)C
    C)D
    D)E
    E)F
    B)G
    G)H
    D)I
    E)J
    J)K
    K)L
    K)YOU
    I)SAN
    """
    system = create_system_from_map(test_map)
    you = system.get_planet("YOU")
    san = system.get_planet("SAN")
    t = Transfer(you, san)
    t.run()
    
    assert t.text_path == ["YOU", "K", "J", "E", "D", "I", "SAN"]
    assert t.required_transfers == 4


def create_system_from_map(starmap):
    """
    COM)B
    B)C
    C)D
    D)E
    E)F
    B)G
    G)H
    D)I
    E)J
    J)K
    K)L
    """
    system = SolarSystem()
    for line in starmap.split("\n"):
        if line.strip() == "":
            continue
        relation = line.split(")")
        parent = relation[0].strip()
        child = relation[1].strip()
        system.add_orbit(parent, child)
    return system




if __name__ == "__main__":
    stars = open("day_6/starmap.txt").read()
    system = create_system_from_map(stars)
    print(f"This system has {system.total_orbits} Orbits.")
    you = system.get_planet("YOU")
    san = system.get_planet("SAN")
    t = Transfer(you, san)
    t.run()
    # 287 is too high?
    print(f"This requires {t.required_transfers} transfers.")
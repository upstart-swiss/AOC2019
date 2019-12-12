import string
from fractions import Fraction
import math

class Map:
    ASTEROID = "#"
    EMPTY = "."
    
    def __init__(self, mapdata, debug=False, **kwargs):
        self._asteroids = []
        self.mapdata = mapdata
        self.grid = self.make_grid(mapdata)
        self.debug = debug
    
    @staticmethod
    def make_grid(mapdata):
        grid = []
        for line in mapdata.split("\n"):
            if line.strip() == '':
                continue
            grid.append(list(line.strip()))
        return grid
    
    def asteroids_seen_from_point(self, source):
        asteroids = []
        for asteroid in self.asteroids:
            if asteroid == source:
                continue
            if self._can_see(source, asteroid):
                asteroids.append(asteroid)
        return asteroids
    
    def _can_see(self, source, dest):
        if self.get_point(dest) != "#":
            print(f"Dest isn't an asteroid - {dest}")
            return False
        source_point = self.get_point(source)
        roid = self._get_blocker(source, dest)
        if roid is not None:
            return False
        if source_point in string.ascii_lowercase:
            print(f"Why wasn't i blocked! {source_point} - {source}")
        # print(f"{source} can see {dest}")
        return True
    
    def _get_blocker(self, source, dest):
        for asteroid in self.asteroids:
            if asteroid == source or asteroid == dest:
                continue
            if self.blocks_point(asteroid, source, dest):
                    if self.debug:
                        print(f"{asteroid} blocks {source} from {dest}")
                    return asteroid
    
    def get_point(self, source):
        return self.grid[source[1]][source[0]]
    
    def blocks_point(self, og_pt, source, og_dest):
        # Adjust to source being 0,0
        if not self.between_points(og_pt, source, og_dest):
            return False
        pt = self.subtract_points(og_pt, source)
        dest = self.subtract_points(og_dest, source)
        # print(f"dest {dest} (og {og_dest}) - pt {pt} (og {og_pt})")
        if (pt[0] == dest[0] and pt[0] == 0) or (pt[1] == dest[1] and pt[1] == 0):
            # print(f"Blocked on a straight line {og_pt}")
            return True
        if (pt[0] == 0 and dest[0] != 0) or (pt[1] ==0 and dest[1] != 0):
            return False
        # print(f"Frac1 - {Fraction(dest[0], dest[1])}")
        if Fraction(dest[0], dest[1]) == Fraction(pt[0], pt[1]):
            return True
        #print(f"Multiplier {multiplier} - dest {dest} - pt {pt}")
        # if (pt[1] * multiplier) == dest[1]:
        #     return True
        return False

    @staticmethod
    def add_points(pt1, pt2):
        return (pt1[0] + pt2[0], pt1[1] + pt2[1])
    
    @staticmethod
    def subtract_points(pt1, pt2):
            return (pt1[0] - pt2[0], pt1[1] - pt2[1])
        
    @staticmethod
    def between_points(pt, pt1, pt2):
        if not (pt1[0] >= pt[0] >= pt2[0] or pt2[0] >= pt[0] >= pt1[0]):
            return False
        if not (pt1[1] >= pt[1] >= pt2[1] or pt2[1] >= pt[1] >= pt1[1]):
            return False
        return True



    @property
    def asteroids(self):
        self._asteroids = []
        for y_index, row in enumerate(self.grid):
            for x_index, x in enumerate(row):
                if x != self.EMPTY:
                    self._asteroids.append((x_index, y_index))
        return self._asteroids


class LaserMap(Map):
    def _angled_shot(self, start, angle, end=None):
        point = start
        print(f"Angled at {angle} from {start}")
        while abs(point[0]) < len(self.grid[0]) and abs(point[1]) < len(self.grid):
            point = (point[0] + angle[0], point[1] + angle[1])
            print(f"pew pew to {point}")
            if abs(point[0]) > 40:
                raise Exception("BIG SCARY")
            if point in self.asteroids:
                print(f"Bang! {point}")
                self.vaporize(point)
                return point

    def laser_shoot(self, start, end):
        print(f"shooting at {end}")
        if start == end:
            print("shooting at yourself")
            return
        elif start[0] == end[0]:
            angle = (0, 1)
        elif start[1] == end[1]:
            angle = (1, 0)
        else:
            frac = Fraction(end[0]-start[0], end[1]-start[1])
            angle = (abs(frac.numerator), abs(frac.denominator))
            print(f"Frac angle {angle} {frac}")
        x_neg = 1
        y_neg = 1
        if end[0] < start[0]:
            x_neg = -1
        if end[1] < start[1]:
            y_neg = -1
        angle = (angle[0] * x_neg, angle[1] * y_neg)
        return self._angled_shot(start, angle, end)
        
    def _asteroids_to_degrees(self, home):
        return [(self._point_to_degrees(home, roid), roid) for roid in self.asteroids]
    
    @staticmethod
    def _point_to_degrees(start, end):
        y = end[1] - start[1]
        x = end[0] - start[0]
        #print(f"{x},{y}")
        return math.atan2(y,x)/math.pi*180

    
    def vaporize(self, point):
        self.grid[point[1]][point[0]] = self.EMPTY
    
    def _next_sucker(self, home, prev_shot):
        asteroids = self._asteroids_to_degrees(home)
        #print(f"Asteroids {asteroids}")
        next_idea = asteroids.copy()
        next_idea.sort()
        for sucker in next_idea:
            if sucker[0] <= prev_shot: 
                continue
            if sucker[1] == home:
                continue
            return sucker

    def spray_and_pray(self, home, end=False):
        vapes = []
        count = 0
        prev_shot = -90.001
        while True:
            sucker = self._next_sucker(home, prev_shot)
            if sucker is None:
                prev_shot = -181
                continue
            prev_shot = sucker[0]
            shot = self.laser_shoot(home, sucker[1])
            if shot is None:
                # raise Exception(f"Shooting thin air! {sucker}")
                print(f"Bad at shooting {sucker}")
                print(f"Remaining roids {len(self.asteroids)}")
                break
            count += 1
            vapes.append(shot)
            if end is not False and count > end:
                return vapes
            if len(self.asteroids) < 3:
                break
        return vapes
                


        
def test_vaporize():
    map1 = """
......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####
"""
    m = LaserMap(map1)
    death = m.laser_shoot((4,4), (9,9))
    assert death == (7,7)
    assert (7,7) not in m.asteroids

def find_most_asteroids(mapdata, **kwargs):
    m = Map(mapdata, **kwargs)
    best_spot = None
    best_count = 0
    for asteroid in m.asteroids:
        seen = len(m.asteroids_seen_from_point(asteroid))
        if seen > best_count:
            print(f"better with {asteroid} - {seen}")
            best_count = seen
            best_spot = asteroid
        elif asteroid == (5,8):
            print(f"5,8 saw {seen}")
    return best_spot


# def test_letters():
#     map1 = """
# #.........
# ...A......
# ...B..a...
# .EDCG....a
# ..F.c.b...
# .....c....
# ..efd.c.gb
# .......c..
# ....f...c.
# ...e..d..c
# """
#     m = find_most_asteroids(map1, debug=True)
    

def test_day10_pt1():
    map1 = """
......#.#.
#..#.#....
..#######.
.#.#.###..
.#..#.....
..#....#.#
#..#....#.
.##.#..###
##...#..#.
.#....####
"""
    assert find_most_asteroids(map1) == (5,8)

def test_day10_map2():
    map2 = """
#.#...#.#.
.###....#.
.#....#...
##.#.#.#.#
....#.#.#.
.##..###.#
..#...##..
..##....##
......#...
.####.###.
"""
    assert find_most_asteroids(map2, debug=True) == (1,2)

def test_day10_map3():
    map3 = """
.#..#..###
####.###.#
....###.#.
..###.##.#
##.##.#.#.
....###..#
..#.#..#.#
#..#.#.###
.##...##.#
.....#.#..
"""
    assert find_most_asteroids(map3) == (6,3)

def test_day10_pt2():
    map4 = """
.#..##.###...#######
##.############..##.
.#.######.########.#
.###.#######.####.#.
#####.##.#.##.###.##
..#####..#.#########
####################
#.####....###.#.#.##
##.#################
#####.##.###..####..
..######..##.#######
####.##.####...##..#
.#####..#.######.###
##...#.##########...
#.##########.#######
.####.#.###.###.#.##
....##.##.###..#####
.#.#.###########.###
#.#.#.#####.####.###
###.##.####.##.#..##
"""
    m = LaserMap(map4)
    shots = m.spray_and_pray((11,13), 200)
    assert shots[0:3] == [(11,12), (12,1), (12,2)]
    assert shots[9] == (12,8)
    assert shots[19] == (16,0)
    assert shots[49] == (16,9)
    assert shots[99] == (10,16)
    assert shots[198] == (9,6)
    assert shots[199] == (8,2)

# def test_day10_map4():
#     map4 = """
# .#..##.###...#######
# ##.############..##.
# .#.######.########.#
# .###.#######.####.#.
# #####.##.#.##.###.##
# ..#####..#.#########
# ####################
# #.####....###.#.#.##
# ##.#################
# #####.##.###..####..
# ..######..##.#######
# ####.##.####...##..#
# .#####..#.######.###
# ##...#.##########...
# #.##########.#######
# .####.#.###.###.#.##
# ....##.##.###..#####
# .#.#.###########.###
# #.#.#.#####.####.###
# ###.##.####.##.#..##
# """
#     assert find_most_asteroids(map4) == (11, 13)

if __name__ == "__main__":
    map1 = """
.#....#####...#..
##...##.#####..##
##...#...#.#####.
..#.....X...###..
..#.#.....#....##
"""

#     map1 = """
# ......#.#.
# #..#.#....
# ..#######.
# .#.#.###..
# .#..#.....
# ..#....#.#
# #..#....#.
# .##.#..###
# ##...#..#.
# .#....####
# """

    map_5 = """
...###.#########.####
.######.###.###.##...
####.########.#####.#
########.####.##.###.
####..#.####.#.#.##..
#.################.##
..######.##.##.#####.
#.####.#####.###.#.##
#####.#########.#####
#####.##..##..#.#####
##.######....########
.#######.#.#########.
.#.##.#.#.#.##.###.##
######...####.#.#.###
###############.#.###
#.#####.##..###.##.#.
##..##..###.#.#######
#..#..########.#.##..
#.#.######.##.##...##
.#.##.#####.#..#####.
#.#.##########..#.##.
"""
    m5 = LaserMap(map_5)
    most = find_most_asteroids(map_5)
    print(f"Most found at {most}") # 11,13
    supershot = m5.spray_and_pray(most, 200)
    print(f"199th shot is {supershot[199]}")

#     m = Map(map1, debug=True)
#     f = m.asteroids_seen_from_point((4,4))
#     #239 too hgih
#     m5 = Map(map_5)
#     most = find_most_asteroids(map_5)
#     m5a = m5.asteroids_seen_from_point(most)
#     print(len(m5a))
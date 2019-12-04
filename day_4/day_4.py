# Password checker
from abc import ABC, abstractmethod

class Password(ABC):
    def __init__(self, password):
        self.valid = False
        self.password = str(password)
        self.run_checks()
    
    def __repr__(self):
        return f"{self.password} - {self.valid}"
    
    def character_counts(self):
        counts = {}
        for character in self.password:
            if character in counts:
                counts[character] += 1
            else:
                counts[character] = 1
        return counts

    def check_decreasing(self):
        maxiumum = 0
        for character in self.password:
            character = int(character)
            if character < maxiumum:
                return False
            elif character > maxiumum:
                maxiumum = character
        return True

    @abstractmethod
    def run_checks(self):
        pass

class Pt1_Pass(Password):
    def run_checks(self):
        if (self.check_decreasing() 
            and len(self.password) == 6
            and self.double_or_more()):
            self.valid = True
        return

    def double_or_more(self):
        counts = self.character_counts()
        for value in counts.values():
            if value >= 2:
                return True
        return False


class Pt2_Pass(Password):
    def run_checks(self):
        if (self.check_decreasing() 
            and len(self.password) == 6
            and self.only_double()):
            self.valid = True

    def only_double(self):
        counts = self.character_counts()
        for value in counts.values():
            if value == 2:
                return True
        return False

def check_range(start, end, password_class=Pt1_Pass):
    start = int(start)
    end = int(end)
    passed = []
    for i in range(start, end+1):
        if password_class(i).valid:
            passed.append(i)
    return passed


def test_checker_pt1():
    assert Pt1_Pass(111111).valid == True
    assert Pt1_Pass(223450).valid == False
    assert Pt1_Pass(123789).valid == False

def test_checker_pt2():
    assert Pt2_Pass(112233).valid == True
    assert Pt2_Pass(123444).valid == False
    assert Pt2_Pass(111122).valid == True

if __name__ == "__main__":
    pt1_total = check_range(158126, 624574)
    print(f"Pt1 Total of {len(pt1_total)}")
    pt2_total = check_range(158126, 624574, Pt2_Pass)
    print(f"Pt2 Total of {len(pt2_total)}")
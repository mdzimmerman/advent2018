from collections import namedtuple, defaultdict, deque
import time
from typing import Dict, Tuple, Set

import numpy as np

Pos = namedtuple("Pos", ["x", "y"])

class Unit:
    ELF, GOBLIN = 0, 1

    def __init__(self, type=ELF, hp=200, ap=3):
        self.type = type
        self.hp = hp
        self.ap = ap

    def as_char(self) -> str:
        if self.type == Unit.ELF:
            return "E"
        elif self.type == Unit.GOBLIN:
            return "G"
        else:
            return "?"

    def as_hp(self) -> str:
        return "%s(%d)" % (self.as_char(), self.hp)

    def __repr__(self):
        typ = None
        if self.type == self.ELF:
            typ = "ELF"
        elif self.type == self.GOBLIN:
            typ = "GOBLIN"
        return "Unit(type=%s hp=%d ap=%d)" % (typ, self.hp, self.ap)

class Map:
    def __init__(self, filename):
        self.filename = filename
        self.nrow = 0
        self.ncol = 0
        self.grid = None
        self.units: Dict[Pos, Unit] = dict()
        self._init_grid(self.filename)

    def _init_grid(self, filename):
        """Initialize the grid."""
        lines = []
        with open(filename, "r") as fh:
            for l in fh:
                l = l.rstrip()
                self.nrow += 1
                if len(l) > self.ncol:
                    self.ncol = len(l)
                lines.append(l)

        buffer = ""
        for l in lines:
            buffer += l.ljust(self.ncol, " ")

        self.grid = np.array([c for c in buffer]).reshape((self.nrow, self.ncol))

        for j in range(self.nrow):
            for i in range(self.ncol):
                if self.grid[j,i] == "G":
                    self.units[Pos(i,j)] = Unit(type=Unit.GOBLIN)
                    self.grid[j,i] = "."
                elif self.grid[j,i] == "E":
                    self.units[Pos(i,j)] = Unit(type=Unit.ELF)
                    self.grid[j,i] = "."

    def get_grid(self, pos: Pos) -> str:
        return self.grid[pos.y, pos.x]

    def print_grid(self, dists: Dict[Pos, int]=dict()):
        for j in range(self.nrow):
            u = []
            for i in range(self.ncol):
                p = Pos(i,j)
                c = self.grid[j,i]
                if p in self.units:
                    c = self.units[p].as_char()
                    u.append(self.units[p].as_hp())
                elif p in dists:
                    c = str(dists[p])
                print(c, end="")
            print("  ", end="")
            print(", ".join(u))

    def neighbors(self, pos: Pos) -> Set[Pos]:
        """Find all neighboring positions of pos that are not rock
        (does not check for the presence of other units)."""
        out = set()
        for dx, dy in [(0, -1), (-1, 0), (1, 0), (0, 1)]:
            nx = pos.x + dx
            ny = pos.y + dy
            if nx < 0 or nx > self.ncol or ny < 0 or ny > self.nrow:
                continue
            npos = Pos(pos.x+dx, pos.y+dy)
            if self.get_grid(npos) == "#":
                continue
            out.add(npos)
        return out

    def dists(self, start: Pos) -> Dict[Pos, int]:
        """Using BFS, calculate distances to all accessible nodes"""
        dists = {start: 0}
        nodes = deque()
        nodes.append(start)
        while nodes:
            node = nodes.popleft()
            for neighbor in self.neighbors(node):
                if neighbor in self.units:
                    continue
                if neighbor not in dists:
                    dists[neighbor] = dists[node]+1
                    nodes.append(neighbor)
        return dists

    def length_of_shortest_path(self, start: Pos, goal: Pos) -> int:
        """Using BFS, calculate shortest distance from start to end"""
        if start == goal:
            return 0
        dists = {start: 0}
        nodes = deque()
        nodes.append(start)
        while nodes:
            node = nodes.popleft()
            for neighbor in self.neighbors(node):
                if neighbor == goal:
                    return dists[node]+1
                if neighbor in self.units:
                    continue
                if neighbor not in dists:
                    dists[neighbor] = dists[node]+1
                    nodes.append(neighbor)

    def get_first_step(self, start: Pos, goal: Pos) -> Pos:
        """For each first step from start, which is the best choice?"""

        # find length of shortest path from each first step to goal
        dist_from_first_step = defaultdict(list)
        for neighbor in self.neighbors(start):
            if neighbor not in self.units:
                d = self.length_of_shortest_path(neighbor, goal)
                if d is not None:
                    dist_from_first_step[d].append(neighbor)

        # for the first steps with the shortest paths, pick the best first
        # step, using reading order to break ties
        if dist_from_first_step:
            dmin = min(dist_from_first_step.keys())
            return sorted(dist_from_first_step[dmin], key=lambda p: (p.y, p.x)).pop(0)
        else:
            return None

    def move(self, start: Pos, unit: Unit) -> Tuple[Pos, str]:
        # check if already in attack range
        for n in self.neighbors(start):
            if n in self.units and self.units[n].type != unit.type:
                return (start, "already in attack range")

        # find possible in-range attack locations to travel to
        inrange = set()
        for epos, enemy in self.units.items():
            if enemy.type == unit.type:
                continue
            for p in self.neighbors(epos):
                if p not in self.units:
                    inrange.add(p)
        #print("inrange: %s" % (inrange,))

        # find accessible attack locations and the distances to each
        dists = self.dists(start)
        inrange_dists = defaultdict(list)
        for p in inrange:
            if p in dists:
                d = dists[p]
                inrange_dists[d].append(p)
        #print("  inrange_dists: %s" % (inrange_dists,))

        # if there are accessible attack locations
        if inrange_dists:
            # pick the closest accessible attack location (ties broken by reading order)
            min_dist = min(inrange_dists.keys())
            dest = sorted(inrange_dists[min_dist], key=lambda p: (p.y, p.x)).pop(0)
            #print("  dest: %s" % (dest,))

            first_step = self.get_first_step(start, dest)
            if first_step is None:
                return (start, "no valid move?")
            #print("  first step: %s" % (first_step,))

            # actually do move
            self.units[first_step] = unit
            del self.units[start]
            return (first_step, "moved %s -> %s" % (start, first_step))
        else:
            return (start, "no valid move")

    def attack(self, pos: Pos, unit: Unit) -> str:
        # find all adjacent enemies and sort by hp
        enemies = defaultdict(list)
        for npos in self.neighbors(pos):
            if npos in self.units and self.units[npos].type != unit.type:
                enemies[self.units[npos].hp].append(npos)
        if not enemies:
            return "no valid targets in attack range"

        # pick the target with the lowest hp, breaking ties in reading order
        min_hp = min(enemies.keys())
        tpos = sorted(enemies[min_hp], key=lambda p: (p.y, p.x)).pop(0)
        target = self.units[tpos]

        # attack that target
        status = "attacking target at %s" % (tpos,)
        target.hp -= unit.ap
        if target.hp <= 0:
            del self.units[tpos]
            status = status + " (unit killed)"
        return status

    def run(self, n: int=None, debug: bool=False, sleep: float=0.0) -> int:
        steps = 0
        while n is None or steps < n:
            if debug:
                print()
                print("-- step %d --" % (steps + 1,))
            no_enemies = False
            for pos in sorted(self.units.keys(), key=lambda p: (p.y, p.x)):
                if pos in self.units: # could have been killed by a prior attack step
                    unit = self.units[pos]
                    enemies = sum([1 for u in self.units.values() if u.type != unit.type])
                    if not enemies:
                        no_enemies = True
                        break
                    npos, mstatus = self.move(pos, unit)
                    astatus = self.attack(npos, unit)
                    if debug:
                        #print("%s %s: move=%s, attack=%s" % (pos, unit, mstatus, astatus))
                        pass
                else:
                    if debug:
                        #print("%s: unit was killed" % (unit,))
                        pass
            if debug:
                self.print_grid()
            if no_enemies:
                break
            else:
                steps += 1
            time.sleep(sleep)

        if debug:
            print()
        hp_remain = sum(u.hp for u in self.units.values())
        print("completed steps=%d, hp remaining=%d" % (steps, hp_remain))
        return hp_remain * steps
        #self.print_grid()



print("## test1: basic movement ##")
t1 = Map("test1.txt")
print(t1.units)
t1.print_grid()
t1.run(n=2, debug=True)

print()
print("## test2: more movement ##")
t2 = Map("test2.txt")
t2.print_grid()
t2.run(n=4, debug=True)

print()
print("## test3: full example ##")
t3 = Map("test3.txt")
print(t3.run(debug=True))

full = ["test4", "test5", "test6", "test7", "test8"]
for f in full:
    print()
    print("## %s ##" % (f,))
    t = Map(f+".txt")
    t.print_grid()
    print(t.run())
    t.print_grid()

print()
print("## input part #1 ##")
inp = Map("input.txt")
inp.print_grid()
print(inp.run(debug=True, sleep=0.0))

#for i in range(1,50):
#    print()
#    print("-- step %d --"  % (i,))
#    t3.step()
#    t3.print_grid()
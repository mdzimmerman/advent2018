from collections import namedtuple, defaultdict
from typing import Dict

import numpy as np

Pos = namedtuple("Pos", ["x", "y"])

class Unit:
    ELF, GOBLIN = 0, 1

    def __init__(self, type=ELF, hp=200, ap=3):
        self.type = type
        self.hp = hp
        self.ap = ap

    def as_char(self):
        if self.type == Unit.ELF:
            return "E"
        elif self.type == Unit.GOBLIN:
            return "G"
        else:
            return None

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

    def get_grid(self, pos: Pos):
        return self.grid[pos.y, pos.x]

    def print_grid(self, dists={}):
        for j in range(self.nrow):
            for i in range(self.ncol):
                p = Pos(i,j)
                c = self.grid[j,i]
                if p in self.units:
                    c = self.units[p].as_char()
                elif p in dists:
                    c = str(dists[p])
                print(c, end="")
            print()

    def neighbors(self, pos: Pos):
        out = set()
        for dx, dy in [(0, -1), (-1, 0), (1, 0), (0, 1)]:
            nx = pos.x + dx
            ny = pos.y + dy
            if nx < 0 or nx >= self.ncol or ny < 0 or ny > self.nrow:
                continue
            npos = Pos(pos.x+dx, pos.y+dy)
            if self.get_grid(npos) == "#":
                continue
            out.add(npos)
        return out

    def dists(self, start: Pos):
        """Using BFS, calculate distances to all accessible nodes"""
        dists = {start: 0}
        nodes = [start]
        while nodes:
            node = nodes.pop(0)
            for neighbor in self.neighbors(node):
                if neighbor in self.units:
                    continue
                if neighbor not in dists:
                    dists[neighbor] = dists[node]+1
                    nodes.append(neighbor)
        return dists

    def all_paths(self, start: Pos, goal: Pos):
        """Using BFS, calculate all non-self crossing paths between start and goal"""
        queue = [(start, [start])]
        while queue:
            (node, path) = queue.pop(0)
            for next in self.neighbors(node) - set(path):
                if next in self.units:
                    continue
                if next == goal:
                    yield path + [next]
                else:
                    queue.append((next, path + [next]))

    def shortest_paths(self, start: Pos, goal: Pos):
        shortest = None
        out = []
        for path in self.all_paths(start, goal):
            if shortest is None:
                shortest = len(path)
            if len(path) == shortest:
                out.append(path)
            else:
                break
        return out

    def move(self, start: Pos, unit: Unit) -> str:
        # check if already in attack range
        for n in self.neighbors(start):
            if n in self.units and self.units[n].type != unit.type:
                return "already in attack range"

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

            # find all shortest paths to chosen destination
            shortest_paths = self.shortest_paths(start, dest)
            first_steps = set()
            for path in shortest_paths:
                first_steps.add(path[1])
            #print("  valid first steps: %s" % (first_steps,))

            # choose the best first step (ties broken by reading order)
            first_step = sorted(first_steps, key=lambda p: (p.y, p.x)).pop(0)
            #print("  first step: %s" % (first_step,))

            # actually do move
            self.units[first_step] = unit
            del self.units[start]
            return "moved %s -> %s" % (start, first_step)
        else:
            return "no valid move"

    def step(self):
        for pos in sorted(self.units.keys(), key=lambda p: (p.y, p.x)):
            unit = self.units[pos]
            status = self.move(pos, unit)
            print("%s %s: %s" % (pos, unit, status))

print("## test1: basic movement ##")
t1 = Map("test1.txt")
print(t1.units)
print()
t1.print_grid()
for _ in range(2):
    print()
    t1.step()
    t1.print_grid()

print()
print("## test2: more movement ##")
t2 = Map("test2.txt")
t2.print_grid()
for _ in range(4):
    print()
    t2.step()
    t2.print_grid()

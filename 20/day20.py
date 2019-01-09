# -*- coding: utf-8 -*-

import networkx

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __str__(self):
        return "P(%d %d)" % (self.x, self.y)
    
    def __repr__(self):
        return "P(%d %d)" % (self.x, self.y)

    def __key(self):
        return (self.x, self.y)  

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        return Point(x, y)

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.__key() == other.__key()
        return NotImplemented
    
    def __ne__(self, other):
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented
    
    def __hash__(self):
        return hash(self.__key())
    
    def neighbor(self, d):
        if d == 'N':
            return Point(self.x, self.y-1)
        elif d == 'E':
            return Point(self.x+1, self.y)
        elif d == 'S':
            return Point(self.x, self.y+1)
        elif d == 'W':
            return Point(self.x-1, self.y)
        else:
            raise Exception("bad direction %s" % (d,))
    
class Maze:
    def __init__(self, regex):
        self.regex = regex
        self.maze = self._build_maze(self.regex)
        
    def _build_maze(self, regex):
        maze = networkx.Graph()
        
        pos = {Point(0, 0)}
        stack = []
        starts, ends = {Point(0, 0)}, set()
       
        for c in regex[1:-1]:
            if c in 'NESW':
                maze.add_edges_from((p, p.neighbor(c)) for p in pos)
                pos = {p.neighbor(c) for p in pos}
            elif c == '(':
                stack.append((starts, ends))
                starts, ends = pos, set()
            elif c == '|':
                ends.update(pos)
                pos = starts
            elif c == ')':
                pos.update(ends)
                starts, ends = stack.pop()
                
        return maze
    
    def pprint(self):
        xmin, xmax = 0, 0
        ymin, ymax = 0, 0
        for n in self.maze.nodes():
            if n.x < xmin: xmin = n.x
            if n.x > xmax: xmax = n.x
            if n.y < ymin: ymin = n.y
            if n.y > ymax: ymax = n.y
            
        print("#", end="")
        for _ in range(xmin, xmax+1):
            print("##", end="")
        print()
        for y in range(ymin, ymax+1):
            print("#", end="")
            for x in range(xmin, xmax+1):
                p = Point(x, y)
                if p == Point(0, 0):
                    print("X", end="")
                else:
                    print(".", end="")
                if p.neighbor('E') in self.maze.adj[p]:
                    print("|", end="")
                else:
                    print("#", end="")
            print()
            print("#", end="")
            for x in range(xmin, xmax+1):
                p = Point(x, y)
                if p.neighbor('S') in self.maze.adj[p]:
                    print("-", end="")
                else:
                    print("#", end="")
                print("#", end="")
            print()
    
    def furthest(self):
        lengths = networkx.algorithms.shortest_path_length(self.maze, Point(0, 0))
        return max(lengths.values())
    
    def count_longer_than(self, n=1000):
        lengths = networkx.algorithms.shortest_path_length(self.maze, Point(0, 0))
        return sum([1 for x in lengths.values() if x >= n])
    
t1 = Maze("^WNE$")

t2 = Maze("^ENWWW(NEEE|SSE(EE|N))$")

t3 = Maze("^ENNWSWW(NEWS|)SSSEEN(WNSE|)EE(SWEN|)NNN$")

t4 = Maze("^ESSWWN(E|NNENN(EESS(WNSE|)SSS|WWWSSSSE(SW|NNNE)))$")

t5 = Maze("^WSSEESWWWNW(S|NENNEEEENN(ESSSSW(NWSW|SSEN)|WSWWN(E|WWS(E|SS))))$")

for m in [t1, t2, t3, t4, t5]:
    print(m.regex)
    print("Furthest room: %d" % m.furthest())
    m.pprint()
    print()
    
indata = open("input.txt").read()
inp = Maze(indata)
inp.pprint()
print("Part #1: %d" % inp.furthest())
print("Part #2: %d" % inp.count_longer_than())
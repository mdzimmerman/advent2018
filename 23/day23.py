# -*- coding: utf-8 -*-

from collections import namedtuple
import re

import numpy as np
import networkx

BoundingBox = namedtuple("BoundingBox", ["xmin", "xmax", "ymin", "ymax", "zmin", "zmax"])

Cube = namedtuple("Cube", ["xmin", "ymin", "zmin", "size"])

class Bot:
    PATT_LINE = re.compile(r"""pos=<(-?\d+),(-?\d+),(-?\d+)>, r=(\d+)""")
    
    def __init__(self, x, y, z, r):
        self.x = x
        self.y = y
        self.z = z
        self.r = r
        
    def __repr__(self):
        return "Bot(pos=<%d,%d,%d> r=%d)" % (self.x, self.y, self.z, self.r)

    def __key(self):
        return (self.x, self.y, self.z, self.r)  

    def __eq__(self, other):
        if isinstance(other, Bot):
            return self.__key() == other.__key()
        return NotImplemented
    
    def __ne__(self, other):
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented
    
    def __hash__(self):
        return hash(self.__key())

    def dist(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y) + abs(self.z - other.z)

    @classmethod
    def parse(cls, s):
        m = cls.PATT_LINE.match(s)
        if m:
            x, y, z, r = (int(n) for n in m.groups())
            return Bot(x, y, z, r)
        else:
            return None

class Graph:
    def __init__(self, filename):
        self.filename = filename
        self.nodes = self._parsefile()
        self.dists = self._calc_dists()
        self.graph = self._build_graph()
        self.bx = np.fromiter((b.x for b in self.nodes), dtype=int)
        self.by = np.fromiter((b.y for b in self.nodes), dtype=int)
        self.bz = np.fromiter((b.z for b in self.nodes), dtype=int)
        self.br = np.fromiter((b.r for b in self.nodes), dtype=int)
        self.n = len(self.nodes)
        
    def _parsefile(self):
        nodes = []
        with open(self.filename, "r") as fh:
            for l in fh:
                bot = Bot.parse(l.rstrip())
                if bot != None:
                    nodes.append(bot)
        return nodes

    def _calc_dists(self):
        dists = {}
        for i in range(len(self.nodes)):
            for j in range(i+1, len(self.nodes)):
                dists[(i,j)] = self.nodes[i].dist(self.nodes[j])
        return dists
    
    def _build_graph(self):
        graph = networkx.MultiDiGraph()
        for i in range(len(self.nodes)):
            graph.add_node(i)
            inode = self.nodes[i]
            for j in range(len(self.nodes)):
                if i == j: continue
                if self.dist(i, j) <= inode.r:
                    graph.add_edge(i, j)
        return graph
    
    def dist(self, i, j):
        """distance between node i and node j"""
        if i > j: 
            i, j = j, i
        return self.dists[(i,j)]
    
    def strongest_adj(self):
        istrong = 0
        rstrong = 0
        for i, n in enumerate(self.nodes):
            if rstrong < n.r:
                istrong = i
                rstrong = n.r
        return len(self.graph.adj[istrong]) + 1

    def bots_bounding_box(self):
        xmin = np.min(self.bx - self.br)
        xmax = np.max(self.bx + self.br)
        ymin = np.min(self.by - self.br)
        ymax = np.max(self.by + self.br)
        zmin = np.min(self.bz - self.br)
        zmax = np.max(self.bz + self.br)
        return BoundingBox(xmin, xmax, ymin, ymax, zmin, zmax)

    def find_initial_cube(self):
        bb = self.bots_bounding_box()
        print(bb)
        c = Cube(bb.xmin, bb.ymin, bb.zmin, 1)
        while (c.xmin + c.size) <= bb.xmax and (c.ymin + c.size) <= bb.ymax and (c.zmin + c.size) <= bb.zmax:
            c = Cube(c.xmin, c.ymin, c.zmin, c.size*2)
        return c

    def bisect(self, c: Cube):
        size2 = c.size // 2
        xmid = c.xmin + size2
        ymid = c.ymin + size2
        zmid = c.zmin + size2

        for x in [c.xmin, xmid]:
            for y in [c.ymin, ymid]:
                for z in [c.zmin, zmid]:
                    yield Cube(x, y, z, size2)

    def score_cube(self, c: Cube):
        d_bots = self.cube_dist_to_bots(c)
        n_intersect = np.sum(d_bots <= self.br)
        d_origin = self.cube_dist_to_origin(c)
        return n_intersect, d_origin

    def cube_dist_to_bots(self, c: Cube):
        dx = self._calc_d(c.xmin, c.size, self.bx)
        dy = self._calc_d(c.ymin, c.size, self.by)
        dz = self._calc_d(c.zmin, c.size, self.bz)
        return dx + dy + dz

    def _calc_d(self, min: int, size: int, b):
        d = np.zeros((self.n, 3), dtype=int)
        d[:,0] = min - b
        d[:,2] = b - (min + size - 1)
        return d.max(1)

    def cube_dist_to_origin(self, c: Cube):
        dx = max(c.xmin, 0, -(c.xmin+c.size-1))
        dy = max(c.ymin, 0, -(c.ymin+c.size-1))
        dz = max(c.zmin, 0, -(c.zmin+c.size-1))
        return dx + dy + dz

    def search(self, cube: Cube):
        if cube.size == 1:
            return cube
        else:
            bestc, bestn, bestd = None, 0, None
            for c in self.bisect(cube):
                n, d = self.score_cube(c)
                if bestc is None or (n > bestn) or (n == bestn and d > bestd):
                    bestc = c
                    bestn = n
                    bestd = d
            print("best: %s %d %d" % (bestc, bestn, bestd))
            return self.search(bestc)

inp = Graph("input.txt")
t2 = Graph("test2.txt")

init = t2.find_initial_cube()
print(init)
t2.search(init)

inp.search(inp.find_initial_cube())
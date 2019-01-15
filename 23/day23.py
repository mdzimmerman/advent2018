# -*- coding: utf-8 -*-

import re
import networkx

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

t = Graph("test.txt")
print(t.strongest_adj())

inp = Graph("input.txt")
print(inp.strongest_adj())
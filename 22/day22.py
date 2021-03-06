# -*- coding: utf-8 -*-

from collections import namedtuple
from heapq import heappush, heappop
import numpy as np

Vertex = namedtuple("Vertex", ["x", "y", "tool"])

class Cave:
    ROCKY, WET, NARROW = 0, 1, 2
    NEITHER, TORCH, CLIMB = 0, 1, 2
    SYMBOL = [".", "=", "|"]
    
    def __init__(self, depth, x, y, pad=5):
        self.depth = depth
        self.xtarget = x
        self.ytarget = y
        self.xmax = x + pad
        self.ymax = y + pad
        self.path = {}
        self._build_erosion_grid()
    
    def _erosion(self, geoindex):
        return (geoindex + self.depth) % 20183
    
    def _build_erosion_grid(self):
        self.erosion = np.zeros((self.ymax+1, self.xmax+1), dtype=int)
        self.erosion[0,0] = self._erosion(0)
        for x in range(1,self.xmax+1):
            self.erosion[0,x] = self._erosion(x * 16807)
        for y in range(1,self.ymax+1):
            self.erosion[y,0] = self._erosion(y * 48271)
        for y in range(1,self.ymax+1):
            for x in range(1,self.xmax+1):
                geo = None
                if x == self.xtarget and y == self.ytarget:
                    geo = 0
                else:
                    geo = self.erosion[y-1,x] * self.erosion[y,x-1]
                self.erosion[y,x] = self._erosion(geo)
        self.grid = self.erosion % 3

    def pprint(self):
        for y in range(0,self.ymax+1):
            for x in range(0,self.xmax+1):
                if x == 0 and y == 0:
                    print("M", end="")
                elif x == self.xtarget and y == self.ytarget:
                    print("T", end="")
                elif (x,y) in self.path:
                    t = self.path[(x,y)]
                    print(t, end="")
                else:
                    print(self.SYMBOL[self.grid[y,x]], end="")
            print()

    def area(self):
        return self.grid[0:self.ytarget+1,0:self.xtarget+1].sum()

    def dijkstra(self):
        time = 0
        v = None
        heap = [(0, Vertex(0, 0, self.TORCH))]
        visited = {Vertex(0, 0, self.TORCH): 0}
        last = {Vertex(0, 0, self.TORCH): None}
        
        while heap:
            time, v = heappop(heap)
            if v.x == self.xtarget and v.y == self.ytarget and v.tool == self.TORCH:
                break

            for tool in [self.NEITHER, self.TORCH, self.CLIMB]:
                if self.grid[v.y, v.x] == tool:
                    continue # can't switch to this tool here
                for x, y in [(v.x-1, v.y), (v.x, v.y-1), (v.x+1, v.y), (v.x, v.y+1)]:
                    if x < 0 or y < 0 or x > self.xmax or y > self.ymax:
                        continue # out of bounds
                    if (self.grid[y,x] == tool):
                        continue # tool disallowed in new vertex
                    vnew = Vertex(x, y, tool)
                    tnew = time+1
                    if tool != v.tool:
                        tnew += 7
                    if vnew in visited and visited[vnew] <= tnew:
                        continue
                    visited[vnew] = tnew
                    last[vnew] = v
                    heappush(heap, (tnew, vnew))

        self.path = {}
        while v in last:
            #print("%4d %s" % (visited[v], v))
            self.path[(v.x, v.y)] = v.tool
            v = last[v]
        return time

t = Cave(510, 10, 10)
ttime = t.dijkstra()
t.pprint()
print("part #1: %d" % (t.area(),))
print("part #2: %d" % (ttime,))
print()

inp = Cave(11817, 9, 751, pad=20)
inptime = inp.dijkstra()
inp.pprint()
print("part #1: %d" % (inp.area(),))
print("part #2: %d" % (inptime,))
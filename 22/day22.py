# -*- coding: utf-8 -*-

import numpy as np

class Cave:
    TYPES = [".", "=", "|"]
    
    def __init__(self, depth, x, y):
        self.depth = depth
        self.xtarget = x
        self.ytarget = y
        self.xmax = x + 5
        self.ymax = y + 5
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
                print(self.TYPES[self.grid[y,x]], end="")
            print()

t = Cave(510, 10, 10)
t.pprint()
print(t.grid[0:11,0:11].sum())

inp = Cave(11817, 9, 751)
print(inp.grid[0:752,0:10].sum())      
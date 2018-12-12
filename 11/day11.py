# -*- coding: utf-8 -*-

import numpy as np

class Grid:
    def __init__(self, serial, gridsize=300):
        self.serial = serial
        self.gridsize = gridsize
        self._init_grid()
        self._init_sumgrid()
        
    def _init_grid(self):
        self.grid = np.zeros((self.gridsize, self.gridsize), dtype=int)
        for i in range(self.gridsize):
            for j in range(self.gridsize):
                x = i + 1
                y = j + 1
                rack_id = x + 10
                power = rack_id * y
                power += self.serial
                power = ((power * rack_id) // 100) % 10
                power -= 5
                self.grid[j,i] = power
    
    @staticmethod
    def bget(grid, i, j):
        if i < 0 or j < 0:
            return 0
        else:
            return grid[j,i]
    
    def _init_sumgrid(self):
        self.sumgrid = np.zeros((self.gridsize, self.gridsize), dtype=int)
        for i in range(self.gridsize):
            for j in range(self.gridsize):
                self.sumgrid[j,i] = (self.bget(self.grid, i, j)
                    + self.bget(self.sumgrid, i, j-1) 
                    + self.bget(self.sumgrid, i-1, j)
                    - self.bget(self.sumgrid, i-1, j-1))
    
    def get(self, x, y):
        return self.grid[y-1,x-1]
    
    def getsum(self, i, j, width):
        return (self.bget(self.sumgrid, i+width-1, j+width-1)
                + self.bget(self.sumgrid, i-1, j-1)
                - self.bget(self.sumgrid, i+width-1, j-1)
                - self.bget(self.sumgrid, i-1, j+width-1))
    
    def findmax(self):
        pmax, xmax, ymax = 0, 0, 0
        for i in range(self.gridsize-2):
            for j in range(self.gridsize-2):
                x = i+1
                y = j+1
                #print(self.grid[j:j+3,i:i+3])
                p = self.getsum(i, j, 3)
                if (p > pmax):
                    pmax = p
                    xmax = x
                    ymax = y
        return pmax, xmax, ymax
    
    def findmaxvar(self):
        pmax, xmax, ymax, smax = 0, 0, 0, 0
        for size in range(3, 301):
            #if (size % 10 == 0):
            #    print(size)
            for i in range(self.gridsize-size-1):
                for j in range(self.gridsize-size-1):
                    x = i+1
                    y = j+1
                    p = self.getsum(i, j, size)
                    if (p > pmax):
                        pmax = p
                        xmax = x
                        ymax = y
                        smax = size
        return pmax, xmax, ymax, smax

tests = [
        ( 8,   3,   5,  4),
        (57, 122,  79, -5),
        (39, 217, 196,  0),
        (71, 101, 153,  4)
        ]
for serial, x, y, expect in tests:
    g = Grid(serial)
    out = g.get(x, y)
    print("Grid(%d).get(%d, %d) should equal %d (%s)" % (serial, x, y, expect, out == expect))

g = Grid(18)
print(g.grid)
print(g.sumgrid)
print("Grid(18) 3x3 power=%d x,y=%d,%d" % g.findmax())
print("Grid(18) NxN power=%d x,y,N=%d,%d,%d" % g.findmaxvar())

g = Grid(42)
print("Grid(42) 3x3 power=%d x,y=%d,%d" % g.findmax())
print("Grid(42) NxN power=%d x,y,N=%d,%d,%d" % g.findmaxvar())

g = Grid(9110)
print("Grid(9110) 3x3 power=%d x,y=%d,%d" % g.findmax())
print("Grid(9110) NxN power=%d x,y,N=%d,%d,%d" % g.findmaxvar())
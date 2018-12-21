# -*- coding: utf-8 -*-

import numpy as np

class Land:
    def __init__(self, filename):
        self.ncol = 0
        self.nrow = 0
        self._init_grid(filename)
        
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
            
        self.grid = np.array([c for c in buffer], 
                             dtype="str").reshape((self.nrow, self.ncol))
    
    def get(self, x, y):
        if x < 0 or x >= self.ncol or y < 0 or y >= self.nrow:
            return ""
        else:
            return self.grid[y,x]
    
    def neighbors(self, x, y):
        d = {'|': 0, '.': 0, '#': 0, '': 0}
        for j in (y-1, y, y+1):
            for i in (x-1, x, x+1):
                if not (i == x and j == y):
                    k = self.get(i, j)
                    d[k] += 1
        return d
    
    def update(self):
        newgrid = np.full((self.nrow, self.ncol), "", dtype="str")
        for j in range(self.ncol):
            for i in range(self.nrow):
                c = self.grid[j,i]
                n = self.neighbors(i,j)
                #print("%s: %s" % (c, n))
                if c == '.':
                    if n['|'] >= 3:
                        newgrid[j,i] = '|'
                    else:
                        newgrid[j,i] = '.'
                elif c == '|':
                    if n['#'] >= 3:
                        newgrid[j,i] = '#'
                    else:
                        newgrid[j,i] = '|'
                elif c == '#':
                    if n['#'] >= 1 and n['|'] >= 1:
                        newgrid[j,i] = '#'
                    else:
                        newgrid[j,i] = '.'
                else:
                    raise Exception("foo")
        #print(newgrid)
        self.grid = newgrid
        
    def updaten(self, n, verbose=False):
        if verbose:
            self.pprint()
        for _ in range(n):
            self.update()
            if verbose:
                print()
                self.pprint()
                            
    def pprint(self):
        for j in range(self.nrow):
            for i in range(self.ncol):
                print(self.grid[j,i], end="")
            print()
            
    def value(self):
        l = (self.grid == '#').sum()
        w = (self.grid == '|').sum()
        #print("%d lumberyards, %d woods" % (l,w))
        return l * w

l = Land("test.txt")
l.updaten(10, verbose=True)
print(l.value())

l2 = Land("input.txt")
l2.updaten(10, verbose=True)
print(l2.value())

l3 = Land("input.txt")
vprev = None
value = l3.value()
i = 0
t = []
v = []
while vprev != value or i < 10000:
    i += 1
    l3.update()
    vprev = value
    value = l3.value()
    print("%8d %8d" % (i, value))
    t.append(i)
    v.append(value)
# -*- coding: utf-8 -*-

import re

import matplotlib.pyplot as plt
import numpy as np

class Vein:
    PAT_INPUT = re.compile(r"""(.)=(\d+), (.)=(\d+)\.\.(\d+)""")
    
    def __init__(self, d1, v1, d2, v2, v3):
        self.xmin = None
        self.xmax = None
        self.ymin = None
        self.ymax = None
        self.type = None
        if (d1 == "x"):
            self.xmin = v1
            self.xmax = v1
            self.ymin = v2
            self.ymax = v3
            self.type = "V"
        elif (d1 == "y"):
            self.xmin = v2
            self.xmax = v3
            self.ymin = v1
            self.ymax = v1
            self.type = "H"
            
    def __repr__(self):
        return "Vein(xmin=%d xmax=%d ymin=%d ymax=%d type=%s)" % (
                self.xmin, self.xmax, self.ymin, self.ymax, self.type)
    
    def offset(self, x, y):
        return self.xmin + x, self.xmax + x, self.ymin + y, self.ymax + y
    
    @staticmethod
    def parse(s):
        m = Vein.PAT_INPUT.match(s)
        if m:
            d1 = m.group(1)
            v1 = int(m.group(2))
            d2 = m.group(3)
            v2 = int(m.group(4))
            v3 = int(m.group(5))
            return Vein(d1, v1, d2, v2, v3)
        else:
            return None

class Ground:
    EMPTY   = 0
    CLAY    = 1
    FLOWING = 2
    SETTLED = 3
    
    def __init__(self, filename):
        self.filename = filename
        self.veins = self._read_veins(self.filename)
        self.xmin, self.xmax, self.ymin, self.ymax = self._calc_bounds()
        self.width  = self.xmax - self.xmin + 1
        self.height = self.ymax - self.ymin + 1
        self.grid = self._build_grid()
    
    def _read_veins(self, filename):
        veins = []
        with open(filename, "r") as fh:
            for l in fh:
                v = Vein.parse(l.rstrip())
                if v != None:
                    veins.append(v)
        return veins
    
    def _calc_bounds(self):
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        for v in self.veins:
            if xmin == None or v.xmin < xmin:
                xmin = v.xmin
            if xmax == None or v.xmax > xmax:
                xmax = v.xmax
            if ymin == None or v.ymin < ymin:
                ymin = v.ymin
            if ymax == None or v.ymax > ymax:
                ymax = v.ymax
        return xmin-1, xmax+1, ymin, ymax

    def _build_grid(self):
        grid = np.zeros(shape=(self.height,self.width), dtype=int)
        for v in self.veins:
            #print(v.offset(-self.xmin, -self.ymin))
            imin, imax, jmin, jmax = v.offset(-self.xmin, -self.ymin)
            grid[jmin:jmax+1,imin:imax+1] = 1
        return grid
    
    def draw_grid(self):
        lines = []
        for j in range(self.height):
            line = []
            for i in range(self.width):
                v = self.grid[j,i]
                if v == self.EMPTY:
                    line.append('.')
                elif v == self.CLAY:
                    line.append('#')
                elif v == self.FLOWING:
                    line.append('|')
                elif v == self.SETTLED:
                    line.append('~')
                else:
                    line.append("?")
            lines.append("".join(line))
        return "\n".join(lines)
    
    def flow(self, x, y, d):
        if x < 0 or x >= self.width:
            return None
        if self.grid[y,x] == self.EMPTY:
            self.grid[y,x] = self.FLOWING
        if y == self.height-1:
            return None
        if self.grid[y,x] == self.CLAY:
            return x
        
        if self.grid[y+1,x] == self.EMPTY:
            self.flow(x, y+1, 0)
        
        if self.grid[y+1,x] == self.SETTLED or self.grid[y+1,x] == self.CLAY:
            if d:
                return self.flow(x+d, y, d)
            else:
                leftx  = self.flow(x-1, y, -1)
                rightx = self.flow(x+1, y,  1)
                if self.grid[y,leftx] == self.CLAY and self.grid[y,rightx] == self.CLAY:
                    self.grid[y,leftx+1:rightx] = self.SETTLED
        else:
            return x
            
    def count_water(self):
        flowing = (self.grid == self.FLOWING).sum()
        settled = (self.grid == self.SETTLED).sum()
        return flowing + settled
    
    def count_settled(self):
        return (self.grid == self.SETTLED).sum()
        
t = Ground("test.txt")

print(t.veins)
print(t.xmin, t.xmax)
print(t.ymin, t.ymax)
#print(t.grid)
print(t.draw_grid())
print()
t.flow(500-t.xmin, 0, 0)
print(t.draw_grid())
print("all: %d" % (t.count_water(),))
print("settled: %d" % (t.count_settled(),))

inp = Ground("input.txt")
inp.flow(500-inp.xmin, 0, 0)
#print(inp.draw_grid())
fig = plt.figure(figsize=(12,60))
ax = fig.add_subplot(111)
#ax.set_xlim([0,250])
#ax.set_ylim([500,0])
ax.imshow(inp.grid)
fig.show()
print("all: %d" % (inp.count_water(),))
print("settled: %d" % (inp.count_settled(),))

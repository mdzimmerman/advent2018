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
        return xmin, xmax, ymin, ymax

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
                if self.grid[j,i] == 0:
                    line.append('.')
                elif self.grid[j,i] == 1:
                    line.append('#')
                elif self.grid[j,i] == 2:
                    line.append('~')
                else:
                    line.append("?")
            lines.append("".join(line))
        return "\n".join(lines)
    
    def fill(self, sx, sy, depth=0):
        x, y = sx, sy
        self.grid[y,x] = 2
        # down
        while y < self.height-1:
            if self.grid[y+1,x] == 0:
                self.grid[y+1,x] = 2
                y += 1
            elif self.grid[y+1,x] == 2:
                return
            elif self.grid[y+1,x] == 1:
                break
        
        leak = False
        while y >= 0 and y < self.height-1 and not leak:
            # fill left
            lx = x
            while lx > 0 and self.grid[y,lx-1] != 1:
                self.grid[y,lx-1] = 2
                if lx-1 == 0:
                    leak = True
                    break
                if self.grid[y+1,lx-1] == 0:
                    leak = True
                    self.fill(lx-1,y,depth+1)
                    break
                lx -= 1
            # fill right
            lx = x
            while lx < self.width-1 and self.grid[y,lx+1] != 1:
                self.grid[y,lx+1] = 2
                if lx+1 == self.width-1:
                    leak = True
                    break
                if self.grid[y+1,lx+1] == 0:
                    leak = True
                    self.fill(lx+1,y,depth+1)
                    break
                lx += 1
            y -= 1
            
    def count_water(self):
        return (self.grid == 2).sum()
        
t = Ground("test.txt")

print(t.veins)
print(t.xmin, t.xmax)
print(t.ymin, t.ymax)
#print(t.grid)
print(t.draw_grid())
print()
t.fill(500-t.xmin, 0)
print(t.draw_grid())
print(t.count_water())

inp = Ground("input.txt")
inp.fill(500-inp.xmin, 0)
#print(inp.draw_grid())
fig = plt.figure(figsize=(16,16))
ax = fig.add_subplot(111)
ax.set_xlim([0,500])
ax.set_ylim([500,0])
ax.imshow(inp.grid)
fig.show()
#plt.imshow(inp.grid)            
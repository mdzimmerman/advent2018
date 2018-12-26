# -*- coding: utf-8 -*-

import re

import numpy as np

class Constellation:
    patt_line = re.compile(r"""position=<\s*(-?\d+),\s+(-?\d+)> velocity=<\s*(-?\d+),\s*(-?\d+)>""")
    
    def __init__(self, filename):
        self.filename = filename
        self.px, self.py, self.vx, self.vy = self._read_file(filename)
        
    def _read_file(self, filename):
        px = []
        py = []
        vx = []
        vy = []
        with open(filename, "r") as fh:
            for l in fh:
                m = self.patt_line.match(l.rstrip())
                if m:
                    px.append(int(m.group(1)))
                    py.append(int(m.group(2)))
                    vx.append(int(m.group(3)))
                    vy.append(int(m.group(4)))
        return np.array(px), np.array(py), np.array(vx), np.array(vy)
    
    def position(self, t):
        return self.px + self.vx * t, self.py + self.vy * t
    
    def find_min_area(self):
        px = self.px
        py = self.py
        area = (max(px) - min(px)) * (max(py) - min(py))
        last_area = area + 1
        t = 0
        while last_area > area:
            lastx, lasty = px, py
            t += 1
            last_area = area
            px, py = self.position(t)
            area = (max(px) - min(px)) * (max(py) - min(py))
            print("%d %d" % (t, area))
        return lastx, lasty
    
t = Constellation("test.txt")
x, y = t.find_min_area()

t2 = Constellation("input.txt")
x2, y2 = t2.find_min_area()
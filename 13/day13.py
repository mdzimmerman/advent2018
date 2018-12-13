# -*- coding: utf-8 -*-

from enum import Enum

import numpy as np

class Dir(Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3

class Cart:    
    def __init__(self, n, x, y, d):
        self.n = n
        self.x = x
        self.y = y
        self.d = d
        self.turns = 0
    
    def __repr__(self):
        return "Cart(n=%d x=%d y=%d d=%s)" % (self.n, self.x, self.y, self.d)
    
    def as_char(self):
        if self.d == Dir.RIGHT:
            return '>'
        elif self.d == Dir.DOWN:
            return 'v'
        elif self.d == Dir.LEFT:
            return '<'
        else:
            return '^'
    
    def advance(self):
        if self.d == Dir.RIGHT:
            self.x += 1
        elif self.d == Dir.DOWN:
            self.y += 1
        elif self.d == Dir.LEFT:
            self.x -= 1
        elif self.d == Dir.UP:
            self.y -= 1
            
    def rotcw(self):
        if self.d == Dir.RIGHT:
            self.d = Dir.DOWN
        elif self.d == Dir.DOWN:
            self.d = Dir.LEFT
        elif self.d == Dir.LEFT:
            self.d = Dir.UP
        elif self.d == Dir.UP:
            self.d = Dir.RIGHT
    
    def rotccw(self):
        if self.d == Dir.RIGHT:
            self.d = Dir.UP
        elif self.d == Dir.UP:
            self.d = Dir.LEFT
        elif self.d == Dir.LEFT:
            self.d = Dir.DOWN
        elif self.d == Dir.DOWN:
            self.d = Dir.RIGHT
    
    def move(self, t):
        if t == '-':
            # just move straight in current direction
            if self.d == Dir.RIGHT or self.d == Dir.LEFT:
                self.advance()
            else:
                raise Exception("bad dir")
        elif t == '|':
            if self.d == Dir.UP or self.d == Dir.DOWN:
                self.advance()
            else:
                raise Exception("bad dir")
        elif t == '/':
            if self.d == Dir.UP or self.d == Dir.DOWN:
                self.rotcw()
                self.advance()
            elif self.d == Dir.LEFT or self.d == Dir.RIGHT:
                self.rotccw()
                self.advance()
            else:
                raise Exception("bad dir")
        elif t == '\\':
            if self.d == Dir.RIGHT or self.d == Dir.LEFT:
                self.rotcw()
                self.advance()
            elif self.d == Dir.UP or self.d == Dir.DOWN:
                self.rotccw()
                self.advance()
            else:
                raise Exception("bad dir")
        else:
            pass  
    
    @staticmethod
    def parsecartdir(c):
        if c == '>':
            return Dir.RIGHT
        elif c == 'v':
            return Dir.DOWN
        elif c == '<':
            return Dir.LEFT
        elif c == '^':
            return Dir.UP
        else:
            return None

class Track:
    def __init__(self, filename):
        self.ncol = 0
        self.nrow = 0
        self._init_grid(filename)
        self._init_carts()
        
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
    
    def _init_carts(self):
        self.carts = []
        self.cart_index = {}
        n = 0
        for j in range(self.nrow):
            for i in range(self.ncol):
                d = Cart.parsecartdir(self.grid[j,i])
                if d != None:
                    self.carts.append(Cart(n, i, j, d))
                    if d == Dir.RIGHT or d == Dir.LEFT:
                        self.grid[j,i] = '-'
                    elif d == Dir.UP or d == Dir.DOWN:
                        self.grid[j,i] = '|'
                    n += 1
        self._index_carts()
    
    def _index_carts(self):
        self.cart_index.clear()
        for c in self.carts:
            i = (c.x, c.y)
            if i not in self.cart_index:
                self.cart_index[i] = []
            self.cart_index[i].append(c)

    def move_carts(self):
        for cart in self.carts:
            t = self.grid[cart.y,cart.x]
            cart.move(t)
        self._index_carts()
                
    def printgrid(self):
        for j in range(self.nrow):
            for i in range(self.ncol):
                if (i, j) in self.cart_index:
                    print(self.cart_index[(i,j)][0].as_char(), end="")
                else:
                    print(self.grid[j,i], end="")
            print()

t = Track("test.txt")
t.printgrid()
for _ in range(10):
    print()
    t.move_carts()
    t.printgrid()
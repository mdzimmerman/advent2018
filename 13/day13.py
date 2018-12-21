# -*- coding: utf-8 -*-

from enum import Enum

import numpy as np

class Dir(Enum):
    UP = 0
    LEFT = 1
    DOWN = 2
    RIGHT = 3

class Cart:
    dir_to_char = {
        Dir.RIGHT: '>',
        Dir.DOWN:  'v',
        Dir.LEFT:  '<',
        Dir.UP:    '^'}
    
    cw = {
        Dir.RIGHT: Dir.DOWN,
        Dir.DOWN:  Dir.LEFT,
        Dir.LEFT:  Dir.UP,
        Dir.UP:    Dir.RIGHT}

    ccw = {
        Dir.RIGHT: Dir.UP,
        Dir.UP:    Dir.LEFT,
        Dir.LEFT:  Dir.DOWN,
        Dir.DOWN:  Dir.RIGHT}
    
    def __init__(self, n, x, y, d):
        self.n = n
        self.x = x
        self.y = y
        self.d = d
        self.inters = 0
    
    def __repr__(self):
        return "Cart(n=%d x=%d y=%d d=%s)" % (self.n, self.x, self.y, self.d)
    
    def as_char(self):
        return self.dir_to_char[self.d]
    
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
        self.d = self.cw[self.d]
    
    def rotccw(self):
        self.d = self.ccw[self.d]
    
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
        elif t == '+':
            i = self.inters % 3
            if i == 0:
                self.rotccw() # turn left
            elif i == 1:
                pass # go straight
            else:
                self.rotcw() # turn left
            self.inters += 1
            self.advance()
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

    def check_collide(self):
        for k, carts in self.cart_index.items():
            (i, j) = k
            if len(carts) > 1:
                print("collision at %d,%d" % (i, j))
                return True
        return False
    
    def remove_collided(self):
        reindex = False
        for j in range(self.nrow):
            for i in range(self.ncol):
                if (i, j) in self.cart
        for k, carts in self.cart_index.items():
            (i, j) = k
            if len(carts) > 1:
                print("collision at %d,%d" % (i, j))
                for c in carts:
                    self.carts.remove(c)
                    reindex = True
        if reindex:
            self._index_carts()

    def printgrid(self):
        for j in range(self.nrow):
            for i in range(self.ncol):
                if (i, j) in self.cart_index:
                    carts = self.cart_index[(i, j)]
                    if len(carts) > 1:
                        print('X', end="")
                    else:
                        print(carts[0].as_char(), end="")
                else:
                    print(self.grid[j,i], end="")
            print()
    
    def run_to_crash(self, verbose=False):
        collision = False
        t = 0
        if verbose:
            print("t=%d" % (t,))
            self.printgrid()
        while not collision:
            self.move_carts()
            t += 1
            if verbose:
                print("t=%d" % (t,))
                self.printgrid()
            collision = self.check_collide()
            
    def run_to_all_crash(self, verbose=False):
        t = 0
        count = len(self.carts)
        if verbose:
            print("t=%d carts=%d" % (t, count))
            self.printgrid()
        while count > 1:   
            for cart in self.carts:
            t = self.grid[cart.y,cart.x]
            cart.move(t)
        self._index_carts()
            self.move_carts()
            t += 1
            if verbose:
                print("t=%d carts=%d" % (t, count))
                self.printgrid()
            self.remove_collided()
            count = len(self.carts)
        self.move_carts()
        print("last cart %s" % (self.carts[0],))
            
t = Track("test.txt")
t.run_to_crash(verbose=True)

inp = Track("input.txt")
inp.run_to_crash()

t2 = Track("test2.txt")
t2.run_to_all_crash(verbose=True)

inp2 = Track("input.txt")
inp2.run_to_all_crash()

#t.printgrid()
#for _ in range(15):
#    print()
#    t.move_carts()
#    t.printgrid()
#    t.check_collide()
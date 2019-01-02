# -*- coding: utf-8 -*-

class ChocChart:
    def __init__(self):
        self.array  = [3, 7]
        self.elfpos = [0, 1]
        self.nelves = len(self.elfpos)
        
    def add_recipe(self):
        s = self.array[self.elfpos[0]] + self.array[self.elfpos[1]]
        if s >= 10:
            self.array.append(1)
        self.array.append(s % 10)
        
    def move_elves(self):
        lenarray = len(self.array)
        for i in range(self.nelves):
            steps = self.array[self.elfpos[i]] + 1
            endsteps = lenarray-1-self.elfpos[i]
            if steps > endsteps:
                steps = steps - endsteps
                self.elfpos[i] = steps % lenarray - 1
            else:
                self.elfpos[i] += steps

    def step(self):
        self.add_recipe()
        self.move_elves()

    def get(self, l, n):
        while len(self.array) < n + l+1:
            self.step()
        return "".join([str(n) for n in self.array[n:n+l]])
        
    def find(self, s):
        window = len(s)
        i = 0
        while s != self.get(window, i):
            i += 1
        return i
    
    def pprint(self):
        for i, n in enumerate(self.array):
            if i == self.elfpos[0]:
                print("(%d)" % (n,), end="")
            elif i == self.elfpos[1]:
                print("[%d]" % (n,), end="")
            else:
                print(" %d " % (n,), end="")
        print()


t = ChocChart()
print("%2d " % (0,), end="")
t.pprint()
for i in range(1,20):
    t.step()
    print("%2d " % (i,), end="")
    t.pprint()

print()
print("part 1")   
for n in [9, 5, 18, 2018, 236021]:
    print("%6d -> %s" % (n, t.get(10, n)))

print()
print("part 2")
for s in ["51589", "01245", "92510", "59414", "236021"]:
    print("%6s -> %d" % (s, t.find(s)))
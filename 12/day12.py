# -*- coding: utf-8 -*-

import re
from collections import deque
from scipy.stats import linregress

class State:
    def __init__(self, s, start):
        self.start = start
        self.deque = deque([c for c in s])
        self.end = start + len(self.deque)

    def first(self):
        i = 0
        c = self.deque[i]
        while c != '#':
            i += 1
            c = self.deque[i]
        return i + self.start

    def last(self):
        i = self.end - 1 - self.start
        c = self.deque[i]
        while c != '#':
            i -= 1
            c = self.deque[i]
        return i + self.start

    def get(self, i):
        if i < self.start or i >= self.end:
            return "."
        else:
            return self.deque[i-self.start]

    def get_window(self, s, e):
        out = []
        for i in range(s, e):
            out.append(self.get(i))
        return "".join(out)

    def pprint(self, start=None, end=None):
        if start == None:
            start = self.start
        if end == None:
            end = self.end
        if start < self.start:
            for _ in range(self.start - start):
                print(".", end="")
        print("".join(self.deque), end="")
        if end > self.end:
            for _ in range(end - self.end):
                print(".", end="")
        print("")
      
    def debug(self):    
        for i in range(self.start-5, self.end+5):
            print("%3d %s" % (i, s.get(i)))
            
    def next(self, rules):
        start = self.first()-3
        out = []
        for i in range(start, self.last()+4):
            window = self.get_window(i-2, i+3)
            if window in rules and rules[window] == '#':
                out.append('#')
            else:
                out.append('.')
            #print("%3d %s => %s" % (i, window, out))
        return State("".join(out), start)

    def score(self):
        s = 0
        for i, c in enumerate(self.deque):
            if c == '#':
                s += (i + self.start)
        return s

def parse(filename):
    patt_state = re.compile(r"""initial state:\s+(.+)""")
    patt_rule = re.compile(r"""(.+) => (.)""")
    state = None
    rules = {}
    with open(filename, "r") as fh:
        m = patt_state.match(fh.readline().rstrip())
        if m:
            state = State(m.group(1), 0)
        fh.readline()
        for l in fh:
            m = patt_rule.match(l.rstrip())
            if m:
                rules[m.group(1)] = m.group(2)
    return state, rules
        
ts, trules = parse("test.txt")

def run_n(state, rules, n=20):
    slist = []
    gen = []
    scores = []
    slist.append(state)
    gen.append(0)
    scores.append(state.score())
    s = state
    for i in range(n):
        s = s.next(rules)
        slist.append(s)
        gen.append(i+1)
        scores.append(s.score())

    #for s in slist:
        #print("%5d " % (s.score(),), end="")
        #s.pprint(start=-10)

    return gen, scores 
    
run_n(ts, trules)

s, rules = parse("input.txt")

gen, scores = run_n(s, rules, 1000) 

lr = linregress(gen[200:1000], scores[200:1000])
print(int(lr.slope * 50_000_000_000) + int(lr.intercept))
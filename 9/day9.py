# -*- coding: utf-8 -*-

from collections import deque

def play(turns=25, nplayers=9, verbose=False):
    c=deque()
    c.append(0)

    scores={}
    p = 0
    for n in range(1,turns+1):
        p = p % nplayers + 1
        if n % 23 == 0 and n > 0:
            if p not in scores:
                scores[p] = 0
            scores[p] += n
            c.rotate(7)
            scores[p] += c.popleft()
        else:
            c.rotate(-2)
            c.appendleft(n)
        if verbose:
            print("%d %s" % (p, c))
    
    return max(scores.values())

print(play(turns=25, nplayers=9, verbose=True))

tests=[
 (10, 1618, 8317),
 (13, 7999, 146373),
 (17, 1104, 2764),
 (21, 6111, 54718),
 (30, 5807, 37305)
]

for p, t, expect in tests:
    calc = play(turns=t, nplayers=p)
    print("p=%d t=%d expect=%d calc=%d" % (p, t, expect, calc))
    
print("Part 1 : %d" % (play(turns=71700, nplayers=405),))

print("Part 2 : %d" % (play(turns=7170000, nplayers=405),))
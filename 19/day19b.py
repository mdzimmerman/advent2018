# -*- coding: utf-8 -*-

reg = [0, 4225, 10551277, 1, 0, 3]
while reg[3] <= reg[2]:
    reg[1] = 1
    while reg[1] <= reg[2]:
        reg[4] = reg[3] * reg[1]
        if reg[4] == reg[2]:
            reg[0] += reg[3]
        else:
            reg[1] += 1
    reg[3] += reg[1]



print(reg)
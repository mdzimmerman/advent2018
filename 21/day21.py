# -*- coding: utf-8 -*-

import re

class Program:
    OPCODES = {
        "addr": lambda reg, a, b : reg[a] + reg[b],
        "addi": lambda reg, a, b : reg[a] + b,
        "mulr": lambda reg, a, b : reg[a] * reg[b],
        "muli": lambda reg, a, b : reg[a] * b,
        "banr": lambda reg, a, b : reg[a] & reg[b],
        "bani": lambda reg, a, b : reg[a] & b,
        "borr": lambda reg, a, b : reg[a] | reg[b],
        "bori": lambda reg, a, b : reg[a] | b,
        "setr": lambda reg, a, b : reg[a],
        "seti": lambda reg, a, b : a,
        "gtir": lambda reg, a, b : 1 if a > reg[b] else 0,
        "gtri": lambda reg, a, b : 1 if reg[a] > b else 0,
        "gtrr": lambda reg, a, b : 1 if reg[a] > reg[b] else 0,
        "eqir": lambda reg, a, b : 1 if a == reg[b] else 0,
        "eqri": lambda reg, a, b : 1 if reg[a] == b else 0,
        "eqrr": lambda reg, a, b : 1 if reg[a] == reg[b] else 0
    }
    
    def __init__(self, filename):
        self.filename = filename
        self.ip, self.instructions = self._parse_file(filename)
        self.instructions_size = len(self.instructions)
        self._reset_reg()
    
    def _parse_file(self, filename):
        ip=None
        instr=[]
        with open(filename, "r") as fh:
            ip_line = fh.readline().rstrip()
            m=re.match(r"""#ip (\d+)""", ip_line)
            if m:
                ip=int(m.group(1))
            for line in fh:
                l=line.rstrip().split(" ")
                instr.append([l[0],int(l[1]),int(l[2]),int(l[3])])
        return ip, instr
    
    def _reset_reg(self):
        self.reg = [0, 0, 0, 0, 0, 0]
       
    def evaluate(self, op, a, b, c):
        self.reg[c] = self.OPCODES[op](self.reg, a, b)
        
    def run(self, debug=0, r0=0):
        self._reset_reg()
        i=0
        self.reg[0]=r0
        seen=set()
        while(self.reg[self.ip] >= 0 and 
              self.reg[self.ip] < self.instructions_size):
            i+=1
            op, a, b, c = self.instructions[self.reg[self.ip]]
            if self.reg[self.ip] == 28:
                nstop = self.reg[5]
                print("%10d %10d" % (i, nstop), end="")
                if nstop not in seen:
                    print(" **")
                    pass
                else:
                    print()
                    return
                seen.add(nstop)
            self.evaluate(op, a, b, c)
            self.reg[self.ip]+=1
        return i
        
inp = Program("input.txt")
inp.run(r0=0)
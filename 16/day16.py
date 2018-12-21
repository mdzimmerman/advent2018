# -*- coding: utf-8 -*-

import re

class Program:
    instr = {
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
    patt_reg = re.compile(r"""(.*):\s+\[(.*)\]""")
    
    def __init__(self, filename):
        self.parsetest(filename)
        self.reduce_opcode_map()
    
    @staticmethod
    def evaluate(op, reg, a, b, c):
        reg[c] = Program.instr[op](reg, a, b)
    
    @staticmethod
    def count_all(breg, op, areg):
        count=0
        ops=[]
        opcode, a, b, c=op
        #print(opcode, a, b, c)
        #print("%2d: " % (opcode,), end="")
        for op in Program.instr:
            r=breg[:]
            Program.evaluate(op, r, a, b, c)
            if r == areg:
                #print(" %s" % (op,), end="")
                ops.append(op)
                count+=1
        #print()
        return ops
    
    @staticmethod
    def get_reg(expname, s):
        m=Program.patt_reg.match(s)
        if m:
            name=m.group(1)
            if expname == name:
                return [int(n) for n in m.group(2).split(", ")]
            return None
        else:
            return None
        
    @staticmethod
    def get_op(s):
        out=[int(n) for n in s.split(" ")]
        return out
    
    def parsetest(self, filename):
        self.count=0
        self.opcode_map={}
        state="examples"
        with open(filename, 'r') as fh:
            lines=[]
            for line in fh:
                lines.append(line.rstrip())
                if state == "examples":
                    if len(lines) == 4:
                        breg=Program.get_reg("Before", lines[0])
                        if breg == None:
                            state="ops"
                            lines.remove("")
                            lines.remove("")
                        else:
                            op=Program.get_op(lines[1])
                            areg=Program.get_reg("After", lines[2])
                            ops=Program.count_all(breg, op, areg)
                        
                            if len(ops) >= 3:
                                self.count+=1
                            opcode = op[0]
                            if opcode not in self.opcode_map:
                                self.opcode_map[opcode]=set(ops)
                            self.opcode_map[opcode] = self.opcode_map[opcode].intersection(ops)
                                #print(breg, op, areg)
                            lines=[]
                elif state == "ops":
                    pass
        self.code=[]
        for l in lines:
            self.code.append([int(n) for n in l.split(" ")])
        print("opcodes with >= 3 ops: %d" % (self.count,))
        return self.count
    
    def reduce_opcode_map(self):
        mult = set()
        sing = set()
        for k, v in self.opcode_map.items():
            if len(v) > 1:
                mult.add(k)
            else:
                sing.add(k)
        
        while len(mult) > 0:
            for s in sing:
                op = self.opcode_map[s]
                for m in mult:
                    self.opcode_map[m] -= op
            #print(p.opcode_map)
            mult = set()
            sing = set()
            for k, v in self.opcode_map.items():
                if len(v) > 1:
                    mult.add(k)
                else:
                    sing.add(k)
                    
        self.n_to_opcode = {}
        for k, v in self.opcode_map.items():
            self.n_to_opcode[k] = v.pop()
   
    def run(self):
        reg = [0, 0, 0, 0]
        for codeline in self.code:
            n, a, b, c = codeline
            opcode = self.n_to_opcode[n]
            Program.evaluate(opcode, reg, a, b, c)
            print("%4s %d %d %d => %s" % (opcode, a, b, c, reg))
        
p = Program("input.txt")

print(p.n_to_opcode)
p.run()

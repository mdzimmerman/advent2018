# -*- coding: utf-8 -*-

import re

class Army:
    PAT_MAIN = re.compile("""(\d+) units each with (\d+) hit points( \(.+\))? with an attack that does (\d+) (.+) damage at initiative (\d+)""")
    PAT_SPECIAL = re.compile("""(.+) to (.+)""")
    
    def __init__(self, units=1, hp=1, immune=set(), weak=set(), attackpower=0, attacktype="", initiative=0):
        self.units = units
        self.hp = hp
        self.immune = immune
        self.weak = weak
        self.attackpower = attackpower
        self.attacktype = attacktype
        self.initiative = initiative
        self.side = None 
        
    def __repr__(self):
        items = ("%s=%r" % (k, v) for k, v in self.__dict__.items())
        return "%s(%s)" % (self.__class__.__name__, ", ".join(items))
        
    @classmethod
    def parse(cls, s):
        m = cls.PAT_MAIN.match(s)
        if m:
            units = int(m.group(1))
            hp = int(m.group(2))
            ap = int(m.group(4))
            at = m.group(5)
            init = int(m.group(6))
            immune = set()
            weak = set()
            
            special = m.group(3)
            if special != None:
                special = special.lstrip()[1:-1]
                for special_clause in special.split("; "):
                    mclause = cls.PAT_SPECIAL.match(special_clause)
                    if mclause:
                        verb = mclause.group(1)
                        for typ in mclause.group(2).split(", "):
                            if verb == 'immune':
                                immune.add(typ)
                            elif verb == 'weak':
                                weak.add(typ)
                        
            
            return Army(units, hp, immune, weak, ap, at, init)
        else:
            return None

class Reindeer:
    def __init__(self, filename):
        self.filename = filename
        self.immune = []
        self.infection = []
        self._parse_file()
        
    def _parse_file(self):
        current = None
        with open(self.filename, "r") as fh:
            for l in fh:
                l = l.rstrip()
                if l == "Immune System:": 
                    current = "immune"
                elif l == "Infection:":
                    current = "infection"
                else:
                    army = Army.parse(l)
                    if army != None:
                        army.side = current
                        if current == "immune":
                            self.immune.append(army)
                        elif current == "infection":
                            self.infection.append(army)

#testparse = [
#   "4555 units each with 9688 hit points (immune to radiation; weak to bludgeoning) with an attack that does 17 radiation damage at initiative 1",
#   "2698 units each with 9598 hit points (immune to slashing) with an attack that does 29 slashing damage at initiative 16",
#   "4682 units each with 6161 hit points with an attack that does 13 radiation damage at initiative 19",
#   "8197 units each with 4985 hit points (weak to cold) with an attack that does 5 cold damage at initiative 18",
#   "582 units each with 3649 hit points with an attack that does 46 slashing damage at initiative 13",
#   "53 units each with 5147 hit points (immune to bludgeoning, slashing) with an attack that does 828 cold damage at initiative 11",
#   "5231 units each with 8051 hit points (weak to radiation) with an attack that does 14 radiation damage at initiative 9",
#   "704 units each with 4351 hit points (immune to cold; weak to slashing) with an attack that does 60 radiation damage at initiative 2",
#   "326 units each with 9157 hit points (weak to cold, slashing) with an attack that does 261 radiation damage at initiative 6",
#   "6980 units each with 3363 hit points (weak to radiation) with an attack that does 4 slashing damage at initiative 4"]
#
#for t in testparse:
#    print(Army.parse(t))
    
test = Reindeer("test.txt")
print(test.immune)
print(test.infection)

     
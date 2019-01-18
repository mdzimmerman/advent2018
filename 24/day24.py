# -*- coding: utf-8 -*-

import re

class Army:
    PAT_MAIN = re.compile("""(\d+) units each with (\d+) hit points( \(.+\))? with an attack that does (\d+) (.+) damage at initiative (\d+)""")
    PAT_SPECIAL = re.compile("""(.+) to (.+)""")
    
    def __init__(self, units=1, hp=1, immune=set(), weak=set(), attackpower=0, attacktype="", initiative=0):
        self.id = None
        self.startunits = units
        self.units = units
        self.hp = hp
        self.immune = immune
        self.weak = weak
        self.attackpower = attackpower
        self.attacktype = attacktype
        self.initiative = initiative
        self.boost = 0
        self.side = None
        
    def __repr__(self):
        items = ("%s=%r" % (k, v) for k, v in self.__dict__.items())
        return "%s(%s)" % (self.__class__.__name__, ", ".join(items))

    def effectivepower(self):
        return self.units * (self.attackpower + self.boost)

    def attackdamage(self, other):
        if self.attacktype in other.immune:
            return 0
        elif self.attacktype in other.weak:
            return 2 * self.effectivepower()
        else:
            return self.effectivepower()

    def reset(self):
        self.units = self.startunits

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
        self.armies = []
        self._parse_file()
        
    def _parse_file(self):
        current = None
        with open(self.filename, "r") as fh:
            n = {"blue": 1, "red": 1}
            for l in fh:
                l = l.rstrip()
                if l == "Immune System:": 
                    current = "blue"
                elif l == "Infection:":
                    current = "red"
                else:
                    army = Army.parse(l)
                    if army != None:
                        army.side = current
                        army.id = n[current]
                        self.armies.append(army)
                        n[current] += 1

    def get_armies(self):
        for x in self.armies:
            if x.units > 0:
                yield x

    def get_armies_by_side(self, side):
        for x in self.armies:
            if x.units > 0 and x.side == side:
                yield x

    def count_by_side(self, side):
        return sum(1 for _ in self.get_armies_by_side(side))
    
    def units_by_side(self, side):
        return sum(x.units for x in self.get_armies_by_side(side))

    def boost(self, boost):
        for x in self.armies:
            if x.side == "blue":
                x.boost = boost

    def reset(self):
        for x in self.armies:
            x.units = x.startunits

    def fight_round(self, boost=0, verbose=False):
        for side in ["blue", "red"]:
            #print(side)
            for a in sorted(self.get_armies_by_side(side), key=lambda x: x.id):
                if verbose: print("%s group %d has %d units" % (side, a.id, a.units))
        if verbose: print()

        assignment = {"blue": {}, "red": {}}
        for aside, dside in [("red", "blue"), ("blue", "red")]:
            if verbose: print("%s => %s" % (aside, dside))
            unpicked = set(self.get_armies_by_side(dside)) 
            for a in sorted(self.get_armies_by_side(aside), key=lambda x: (-x.effectivepower(), -x.initiative) ):
                dbest = None
                for d in unpicked:
                    dmg = a.attackdamage(d)
                    if verbose: print("%s => %s (%d dmg)" % (a.id, d.id, dmg))
                    if dbest == None:
                        if dmg > 0:
                            dbest = d
                    else:
                        if dmg > a.attackdamage(dbest):
                            dbest = d
                        elif dmg == a.attackdamage(dbest) and d.effectivepower() > dbest.effectivepower():
                            dbest = d
                        elif dmg == a.attackdamage(dbest) and d.effectivepower() == dbest.effectivepower() and d.initiative > dbest.initiative:
                            dbest = d
                if dbest == None:
                    assignment[aside][a.id] = None
                else:
                    assignment[aside][a.id] = dbest
                    unpicked.remove(dbest)
        if verbose: print()
        
        for a in sorted(self.get_armies(), key=lambda x: -x.initiative):
            d = assignment[a.side][a.id]
            if d == None:
                if verbose: print("%s group %d doesn't attack" % (a.side, a.id))
            else:
                dmg = a.attackdamage(d)
                dlost = dmg // d.hp
                if dlost > d.units:
                    dlost = d.units
                d.units -= dlost
                if verbose: print("%s group %d attacks %s group %d, killing %d" % (a.side, a.id, d.side, d.id, dlost))
        if verbose: print()

    def fight(self, boost=0, verbose=False):
        self.reset()
        self.boost(boost)
        nred  = 0
        nblue = 0
        while self.count_by_side("red") > 0 and self.count_by_side("blue") > 0:
            self.fight_round(boost=boost, verbose=verbose)
            nrednew  = self.units_by_side("red")
            nbluenew = self.units_by_side("blue")
            if nrednew == nred and nbluenew == nblue:
                break
            else:
                nred  = nrednew
                nblue = nbluenew
        return ("%d-%d" % (nblue, nred), nblue - nred)

test = Reindeer("test.txt")
for b in range(0, 1600):
    print("%4d %s" % (b, test.fight(boost=b)))

inp = Reindeer("input.txt")
for b in range(0, 50):
    print("%4d %s" % (b, inp.fight(boost=b)))    

     
import json

data = None

#Generated by eat.py
with open('stuff.json') as fp:
    data = json.load(fp)

#Stuff we have (where the calculator should stop), incl. tools
wehave = ("Craft-Table","Chair for the Head","Bandar Toolkit","Flotsam","Better Bitterbean","Shiny Rock","Magical Dungbeetle","Widow's Whisp Berries","Little Bit O' Nothing",
"Worthless Putrid Leather","Rickety Reeds","Clump of Dry Grass","Bird's Nest","Three-Pointed Thorn","Polished Small Stone","Solid Branch","Abandoned Eggs","Wooly Mushroom","Rotten Fruit",
"Swarming Grub","Coarse Frangible Thread","Boulder","Spicy Moss")

# Actions we want to accept for resource resolving. For example 'Extract' would be for mining, we don't need that.
actions = ('Tinker','Combine','McGuyver')

#target = 'Slithy Tove'
#target = "Base Metal Studs"
#target = "Bandar Toolkit"
#target = "Chair for the Head"
#target = "Multifunctional Samovar"
target = "Stone Pickaxe"


def solve(data, solved, target):
    """If found matching recipe for target in data, recursively adds the stuff
    we have into resolved list and stuff not known how to obtain into unsolved list.
    Returns dicts of solved and unsolved stuff"""
    nsolved = {}
    nunsolv = {}
    for d in data:
        (dk,dv) = next(iter(d.items()))
        if dv["action"] not in actions:
            continue
        if dk == target:
            print("Considering '%s': %s" % (dk, dv))
            for (req,qty) in dv.items():
                if req == 'action':
                    continue
                if req in wehave or req in nsolved or req in solved:
                    nsolved[req] = nsolved.get(req,0) + qty
                else:
                    (ressolv, resunsolv) = solve(data,nsolved,req)
                    #newly resolved stuff
                    for nk in ressolv.keys():
                        # was previously unsolved, multiply by unsolved req
                        print("Resolved %d '%s' per 1 '%s'" % (ressolv[nk], nk, req))
                        nsolved[nk] = nsolved.get(nk,0) + qty*ressolv[nk]
                    for nk in resunsolv.keys():
                        # was previously unsolved, multiply by unsolved req
                        print("Unsolved %d '%s' per 1 '%s'" % (resunsolv[nk], nk, req))
                        nunsolv[nk] = nunsolv.get(nk,0) + qty*resunsolv[nk]
    if len(nsolved) == 0:
        nunsolv[target] = 1

    return (nsolved, nunsolv)

print(solve(data,{},target))

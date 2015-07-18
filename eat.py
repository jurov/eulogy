import sys
import re
from xml.dom import minidom
import json

def rl(f):
    line = f.readline()
    if line:
        line = line[25:].strip()
    else:
        line = None
    return line

"""1st argument as eulora log filename, with USER logging enabled.
To have all recipes dumped into the log, you must read them.
To have merchant/storage dumped, open these windows."""

WHAT = re.compile('-- (.+?) -----')
COMBINE = re.compile('(?:between )?([0-9]+) (?:and [0-9]+ )?(.+)s$')
EXTRACT = re.compile('Extract with (.+?) into(?: into)? some (.+?)s using (.+?)\.')
DO = re.compile('(.+?) with (.+?) into (.+?) using (.+?)(?: with a (.+?))?\.')
output = set()
prices = {}
with open(sys.argv[1]) as f:
    while True:
        line = rl(f)
        what = None
        if line is None:
            break
        if(line.endswith('CRAFT_INFO:')):
            res = WHAT.match(rl(f))
            if not res:
                break
            #print("what:" + res.group(1))
            what = res.group(1)
            while True:
                line = rl(f)
                combines = [x.strip() for x in line.split(',')]
                into = None
                if combines[0].startswith('Combine'):
                    combines[0] = combines[0][8:]
                    if combines[-1].startswith('into '):
                        into = combines[-1][5:-1]
                        combines = combines[:-1]
                        #print("into: " + into)
                    else:
                        break
                    cres = []
                    for c in combines:
                        res = COMBINE.match(c)
                        if res:
                            cres.append((res.group(2) ,int(res.group(1))))
                        else:
                            cres.append(c)
                    #print("combine: %s" % cres)
                    rr = (into,'Combine', tuple(cres))
                    output.add(rr)
                elif line.find(' into ') > 0:
                    res = EXTRACT.match(line)
                    r = None
                    if res:
                        r = ({'action': 'Extract', 'bundle': res.group(1) , 'result': res.group(2), 'use' : [res.group(3)]})
                        # we already have the marker
                        #prices.update({res.group(3): 0})
                        output.add((res.group(3),'Explore'))
                        rr = (res.group(2), 'Extract', (res.group(1),res.group(3)))
                    else:
                        res = DO.match(line)
                        if res:
                            r = ({'action': res.group(1), 'bundle': res.group(2) , 'result': res.group(3), 'use' : []})
                            uses = [res.group(2), res.group(4)]
                            if res.lastindex == 5:
                                uses.append(res.group(5))
                            rr = (res.group(3), res.group(1), tuple(uses))
                    output.add(rr)
                else:
                    break
        elif line.endswith('MERCHANT: Buy'):
            while True :
                line = rl(f)
                if not line:
                    line = rl(f)
                if not line:
                    break
                pos = line.find('<L>')
                if pos < 0:
                    break
                xmldoc = minidom.parseString(line[pos:])
                for item in xmldoc.getElementsByTagName('ITEM'):
                    name = item.attributes['NAME'].value
                    price = int(item.attributes['PRICE'].value)
                    if(price < prices.get(name,99999999)):
                        prices.update({ name : price })

#prices['Craft-Table'] = 0
jout = []
for o in output:
    item = {'action' : o[1]}
    if len(o) > 2:
        for r in o[2]:
            if isinstance(r,str):
                item[r] = 1
            else:
                item[r[0]] = r[1]
    jout.append({o[0] : item})

with open('stuff.json','w') as jsonfp:
    json.dump(jout,jsonfp,indent=0)

for name in prices.keys():
    rr = (name, 'Buy', (('coppers', prices[name]),))
    output.add(rr)
#Nothing done yet with prices



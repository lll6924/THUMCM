import pandas as pd
import os
import numpy as np
import re
from match import *
import math

def getdata(id):
    toload=None
    for file in os.listdir("data"):
        if re.match("^"+str(id)+".*",file):
            toload=file
            break
    assert(toload is not None)
    print("loading ",toload)
    dframe=pd.read_excel(os.path.join('data',toload),dtype=np.str)
    scores=[]
    for i,d in zip(range(len(dframe)),dframe):
        if(i==16):
            scores=dframe[d]
    assert(len(scores)>0)
    sets=[]
    points=[]
    setma=0
    setfan=0
    scorema=0
    scorefan=0
    for (index,row),res in zip(dframe.iterrows(),scores):
        if(res in['樊得','马得']):
            bats=[]
            last=None
            for r in row[1:]:
                r=str(r).replace(' ',"")
                if len(r)<1:
                    continue
                if not re.match("nan",r) and not r in ['樊得','马得']:
                    b=None
                    if re.match("^[abcd]-(A1|A2|B1|B2|C1|C2)$",r):
                        b=bat(type=0,method=r[0],fall=r[2:])
                    elif re.match("^[abcd]$",r):
                        b=bat(type=1,method=r)
                    elif re.match("^\d+-[ABCD]$",r):
                        b=bat(type=2,method=r[0:-2],fall=r[-1],last=last)
                    elif re.match("^\d+$",r):
                        b=bat(type=3,method=r,last=last)
                    if b is None:
                        print("report outlier",setma, setfan, scorema, scorefan, r, res)
                        continue
                    bats.append(b)
                    last=b
            winner="fan" if res=='樊得' else "ma"
            p=point(bats,winner,scorema,scorefan)
            if winner=='fan':
                scorefan+=1
            else:
                scorema+=1
            points.append(p)
        else:
            if len(points)>0:
                s=set(points,setma,setfan)
                points=[]
                sets.append(s)
                if(scorema>scorefan):
                    setma=setma+1
                else:
                    setfan=setfan+1
                scorema=0
                scorefan=0
    m=match(sets)
    return m

if __name__=="__main__":
    getdata(0)
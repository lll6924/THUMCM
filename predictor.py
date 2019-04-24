import random
from match import another,extract
import math

class predictor:
    def __init__(self):
        self._predictor={}
        self._yset=set()
    def train(self,x,y,w):
        self._yset.add(y)
        if not x in self._predictor.keys():
            self._predictor[x]={}
        if not y in self._predictor[x].keys():
            self._predictor[x][y]={"win":0.,"total":0.}
        self._predictor[x][y]["total"]+=1
        if w==1:
            self._predictor[x][y]["win"]+=1
    def predict(self,x):
        if not x in self._predictor.keys():
            sp=random.sample(list(self._yset),1)
            return 0.5,sp[0]
        mx=-1
        ret=-1
        for k in self._predictor[x].keys():
            w=self._predictor[x][k]
            if w["total"]>4 and w["win"]/w["total"]>mx:
                mx=w["win"]/w["total"]
                ret=k
        if mx==-1:
            sp = random.sample(list(self._yset), 1)
            return 0.5, sp[0]
        return mx,ret
    def valueof(self,x,y):
        if not x in self._predictor.keys():
            return 0.5
        if not y in self._predictor[x].keys():
            return 0.5
        w=self._predictor[x][y]
        return w["win"]/w["total"]

def predict(matches):
    ma_predictor=predictor()
    fan_predictor=predictor()
    for j in range(len(matches)):
        if(j==2):
            continue
        m=matches[j]
        for s in m._sets:
            for p in s._points:
                last="begin"
                for i in range(len(p._bats)):
                    if (p._server == "ma" and (i % 2) == 0) or (p._server == "fan" and (i % 2) == 1):
                        ma_predictor.train(last,extract(p._bats[i]),int(p._winner=="ma"))
                    else:
                        fan_predictor.train(last, extract(p._bats[i]), int(p._winner == "fan"))
                    last=extract(p._bats[i])

    m=matches[2]
    all=0
    correct=0
    for s in m._sets:
        for p in s._points:
            turn = p._server
            last="begin"
            for i in range(len(p._bats)):
                if turn=="ma":
                    value=ma_predictor.valueof(last,extract(p._bats[i]))
                    print(turn,value)
                    value0,play=ma_predictor.predict(last)
                    all+=1
                    if abs(value-value0)<1e-8:
                        correct+=1
                else:
                    value=fan_predictor.valueof(last,extract(p._bats[i]))
                    print(turn,value)
                    value0,play=fan_predictor.predict(last)
                    all+=1
                    if abs(value-value0)<1e-8:
                        correct+=1
                turn=another(turn)
                last = extract(p._bats[i])
            print()
    print(correct/all)


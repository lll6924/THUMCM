import math
def another(str):
    if(str=="ma"):
        return "fan"
    return "ma"

def extract(bat):
    if bat._fall is None:
        return bat._method
    else:
        return bat._method + '-' + bat._fall
class bat:
    def __init__(self,type,method,fall=None,last=None):
        #print(type,method,fall)
        self._type=type # 1 for success_serve; 1 for failure_serve; 2 for success_strike; 3 for failure_strike
        self._method=method
        self._fall=fall
        self._last=last
class point:
    def __init__(self,bats,winner,scorema,scorefan):#scorema & scorefan are the score before this point
        self._bats=bats[:]
        self._winner=winner
        self._n=len(bats)
        if(bats[-1]._type==0):
            self._server=self._winner
        elif(bats[-1]._type==1):
            self._server=another(self._winner)
        elif(bats[-1]._type==2):
            if(self._n %2==0):
                self._server=another(self._winner)
            else:
                self._server=self._winner
        else:
            if(self._n %2==1):
                self._server=another(self._winner)
            else:
                self._server=self._winner
        if self._server==self._winner and len(self._bats)%2==0:
            self._bats[-1].type=3
        if self._server != self._winner and len(self._bats) % 2 == 1:
            self._bats[-1].type = 3

        self._scorema=scorema
        self._scorefan=scorefan

class set:
    def __init__(self,points,setma,setfan):#scorema & scorefan are the set score before this set
        self._points=points[:]
        self._n=len(points)
        #for correctness
        rg=min(20,len(points)-1)
        if (len(points) > 2 and points[0]._server != points[1]._server):
            if(points[1]._server!=points[2]._server):
                points[0]._server = another(points[2]._server)
            else:
                points[1]._server = another(points[2]._server)

        for i in range(rg):
            if((i//2)%2==0):
                points[i]._server=points[0]._server
            else:
                points[i]._server = another(points[0]._server)
        for p in points:
            p.set=self

        #print(points[0]._server)
        self._setma=setma
        self._setfan=setfan

class match:
    def __init__(self,sets):
        self._sets=sets[:]
        self._n=len(sets)
        for s in sets:
            s.match=match
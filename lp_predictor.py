import numpy as np
from match import *
from scipy.optimize import linprog

ma_serves={}
ma_serveid=0
ma_backs={}
ma_backid=0

fan_serves={}
fan_serveid=0
fan_backs={}
fan_backid=0

def register(kind,name):
    global ma_backid
    global ma_serveid
    global fan_backid
    global fan_serveid
    name=name._method
    if(kind=="ma_serve"):
        if not name in ma_serves.keys():
            ma_serves[name]=ma_serveid
            ma_serveid+=1
    elif(kind=="ma_back"):
        if not name in ma_backs.keys():
            ma_backs[name]=ma_backid
            ma_backid+=1
    elif (kind == "fan_serve"):
        if not name in fan_serves.keys():
            fan_serves[name] = fan_serveid
            fan_serveid += 1
    elif (kind == "fan_back"):
        if not name in fan_backs.keys():
            fan_backs[name] = fan_backid
            fan_backid += 1

def getserveid(name,serve):
    serve=serve._method
    if(name=="fan"):
        return fan_serves[serve]
    else:
        return ma_serves[serve]

def getbackid(name,back):
    back=back._method
    if(name=="fan"):
        return fan_backs[back]
    else:
        return ma_backs[back]

def lp_predict(matches):
    A_ub=[]
    b_ub=[]
    for j in range(len(matches)):
        m=matches[j]
        for s in m._sets:
            for p in s._points:
                if(len(p._bats)<2):
                    continue
                turn=p._server
                for i in range(len(p._bats)):
                    bat=p._bats[i]
                    if bat._type == 3 or bat._type==1:
                        continue
                    if(i==0):
                        if p._server=="ma":
                            register("ma_serve",bat)
                        else:
                            register("fan_serve",bat)
                    else:
                        if turn=="ma":
                            register("ma_back",bat)
                        else:
                            register("fan_back",bat)
                    turn=another(turn)
    print(ma_serveid)
    print(ma_backid)
    print(fan_serveid)
    print(fan_backid)
    a=ma_serveid
    b=ma_backid
    c=fan_serveid
    d=fan_backid
    N=a+b*c+b*d+c+d*a+d*b
    target=np.zeros(N,dtype=np.float)
    mf=0
    mj=a
    mh=a+b*c
    ff=a+b*c+b*d
    fj=a+b*c+b*d+c
    fh=a+b*c+b*d+c+d*a
    added=0
    for j in range(len(matches)):
        if(j!=1):
            continue
        m=matches[j]
        for s in m._sets:
            for p in s._points:
                if(len(p._bats)<2):
                    continue
                turn=p._server
                toadd = np.zeros(N, dtype=np.float)
                constant = 0.5
                last = None
                for i in range(len(p._bats)):
                    bat=p._bats[i]
                    if bat._type==1 or bat._type==3:
                        continue
                    if p._winner=="ma":
                        if(i==0):
                            if(turn=="fan"):
                                toadd[getserveid(turn,bat)+ff]-=1
                            else:
                                toadd[getserveid(turn,bat)+mf]+=1
                        elif(i==1):
                            serve = getserveid(another(turn), last)
                            back = getbackid(turn, bat)
                            if(turn=="fan"):
                                toadd[fj+serve*d+back]-=1
                            else:
                                toadd[mj+serve*b+back]+=1
                        else:
                            backlast = getbackid(another(turn), last)
                            back = getbackid(turn, bat)
                            if (turn == "fan"):
                                toadd[fh + backlast * d + back] -= 1
                            else:
                                toadd[mh + backlast * b + back] += 1
                    else:
                        if (i == 0):
                            if (turn == "fan"):
                                toadd[getserveid(turn, bat) + ff] += 1
                            else:
                                toadd[getserveid(turn, bat) + mf] -= 1
                        elif (i == 1):
                            serve = getserveid(another(turn), last)
                            back = getbackid(turn, bat)
                            if (turn == "fan"):
                                toadd[fj + serve * d + back] += 1
                            else:
                                toadd[mj + serve * b + back] -= 1
                        else:
                            backlast = getbackid(another(turn), last)
                            back = getbackid(turn, bat)
                            if (turn == "fan"):
                                toadd[fh + backlast * d + back] += 1
                            else:
                                toadd[mh + backlast * b + back] -= 1
                    A_ub.append(toadd.copy())
                    b_ub.append(1.-constant)
                    A_ub.append(-toadd.copy())
                    b_ub.append(constant)
                    last=bat
                    turn=another(turn)
                if last is not None:
                    target-=toadd
                    added+=1
    print(np.asarray(A_ub).shape)
    target=target/added
    #print(target)
    ans=linprog(target,A_ub,b_ub)
    print(ans)
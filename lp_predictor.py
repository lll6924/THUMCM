import numpy as np
from match import *
from scipy.optimize import linprog
import pandas as pd
import os

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
    name=extract(name)
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
    serve=extract(serve)
    if(name=="fan"):
        return fan_serves[serve]
    else:
        return ma_serves[serve]

def getbackid(name,back):
    back=extract(back)
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
    counts=np.zeros(N,dtype=np.float)
    mf=0
    mj=a
    mh=a+b*c
    ff=a+b*c+b*d
    fj=a+b*c+b*d+c
    fh=a+b*c+b*d+c+d*a
    added=0
    for j in range(len(matches)):
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
                                counts[getserveid(turn,bat)+ff]+=1
                            else:
                                toadd[getserveid(turn,bat)+mf]+=1
                                counts[getserveid(turn,bat)+mf]+=1
                        elif(i==1):
                            serve = getserveid(another(turn), last)
                            back = getbackid(turn, bat)
                            if(turn=="fan"):
                                toadd[fj+serve*d+back]-=1
                                counts[fj+serve*d+back]+=1
                            else:
                                toadd[mj+serve*b+back]+=1
                                counts[mj+serve*b+back] += 1
                        else:
                            backlast = getbackid(another(turn), last)
                            back = getbackid(turn, bat)
                            if (turn == "fan"):
                                toadd[fh + backlast * d + back] -= 1
                                counts[fh + backlast * d + back] += 1
                            else:
                                toadd[mh + backlast * b + back] += 1
                                counts[mh + backlast * b + back] += 1
                    else:
                        if (i == 0):
                            if (turn == "fan"):
                                toadd[getserveid(turn, bat) + ff] += 1
                                counts[getserveid(turn, bat) + ff] += 1
                            else:
                                toadd[getserveid(turn, bat) + mf] -= 1
                                counts[getserveid(turn, bat) + mf] += 1
                        elif (i == 1):
                            serve = getserveid(another(turn), last)
                            back = getbackid(turn, bat)
                            if (turn == "fan"):
                                toadd[fj + serve * d + back] += 1
                                counts[fj + serve * d + back] += 1
                            else:
                                toadd[mj + serve * b + back] -= 1
                                counts[mj + serve * b + back] += 1
                        else:
                            backlast = getbackid(another(turn), last)
                            back = getbackid(turn, bat)
                            if (turn == "fan"):
                                toadd[fh + backlast * d + back] += 1
                                counts[fh + backlast * d + back] += 1
                            else:
                                toadd[mh + backlast * b + back] -= 1
                                counts[mh + backlast * b + back] += 1
                    A_ub.append(toadd.copy())
                    b_ub.append(1.-constant)
                    A_ub.append(-toadd.copy())
                    b_ub.append(constant)
                    last=bat
                    turn=another(turn)
                if last is not None and j!=2:
                    target-=toadd
                    added+=1
    columns=[]
    A_ub=np.asarray(A_ub,dtype=np.float)
    for i in range(A_ub.shape[1]):
        zer=True
        for j in range(A_ub.shape[0]):
            if A_ub[j,i]!=0:
                zer=False
                break
        if zer==False:
            columns.append(i)
    A_ub=A_ub[...,columns]
    #print(A_ub)
    #print(np.asarray(A_ub).shape)
    target=target/added
    target=target[columns]
    #print(target)
    ans=linprog(target,A_ub,b_ub,bounds=(-1,1),method='interior-point',options={"disp":True})
    x=ans['x']
    xs=np.zeros(N,dtype=float)
    for C,x in zip(columns,x):
        xs[C]=x
    if not os.path.exists("analyze"):
        os.mkdir("analyze")
    #print(xs.shape,np.asarray(xs[:mj]),ma_serves.keys())
    mfs=pd.DataFrame(np.asarray(xs[:mj]),index=ma_serves.keys())
    mfs.to_csv(os.path.join("analyze","ma_serve.csv"))
    mjs=pd.DataFrame(np.asarray(xs[mj:mh]).reshape(c,b),columns=ma_backs.keys(),index=fan_serves.keys())
    mjs.to_csv(os.path.join("analyze","ma_anti_serve.csv"))
    mhs=pd.DataFrame(np.asarray(xs[mh:ff]).reshape(d,b),index=fan_backs.keys(),columns=ma_backs.keys())
    mhs.to_csv(os.path.join("analyze", "ma_back.csv"))
    ffs=pd.DataFrame(np.asarray(xs[ff:fj]),index=fan_serves.keys())
    ffs.to_csv(os.path.join("analyze", "fan_serve.csv"))
    fjs=pd.DataFrame(np.asarray(xs[fj:fh]).reshape(a,d),index=ma_serves.keys(),columns=fan_backs.keys())
    fjs.to_csv(os.path.join("analyze", "fan_anti_serve.csv"))
    fhs=pd.DataFrame(np.asarray(xs[fh:N]).reshape(b,d),index=ma_backs.keys(),columns=fan_backs.keys())
    fhs.to_csv(os.path.join("analyze", "fan_back.csv"))

    for i in range(b):
        for j in range(d):
            score=xs[fh+i*d+j]
            number=counts[fh+i*d+j]
            if (score>0.2 and number<8 and number>1) or (score<-0.2 and number>1):
                print("use ",list(fan_backs.keys())[j],"to counter ",list(ma_backs.keys())[i],"score=",score,"number=",number)

    print(ans)
    all=0
    correct=0
    for j in range(len(matches)):
        if(j!=2):
            continue
        m=matches[j]
        for s in m._sets:
            for p in s._points:
                if(len(p._bats)<2):
                    continue
                turn=p._server
                last = None
                score=0.5
                for i in range(len(p._bats)):
                    bat=p._bats[i]
                    if bat._type==1 or bat._type==3:
                        continue
                    if (i == 0):
                        if (turn == "fan"):
                            score-=xs[getserveid(turn, bat) + ff]
                        else:
                            score+=xs[getserveid(turn, bat) + mf]
                    elif (i == 1):
                        serve = getserveid(another(turn), last)
                        back = getbackid(turn, bat)
                        if (turn == "fan"):
                            score-=xs[fj + serve * d + back]
                        else:
                            score+=xs[mj + serve * b + back]
                    else:
                        backlast = getbackid(another(turn), last)
                        back = getbackid(turn, bat)
                        if (turn == "fan"):
                            score-=xs[fh + backlast * d + back]
                        else:
                            score+=xs[mh + backlast * b + back]
                    print(turn,score)
                    turn=another(turn)
                    last=bat
                print()
                all+=1
                #print(p._winner,score)
                if (p._winner=='ma' and score>0.5)or(p._winner=='fan'and score<=0.5):
                    correct+=1
    print(correct/all)

from dataset import *
from match import *
from predictor import *
from lp_predictor import *
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import os
from matplotlib.ticker import MaxNLocator

NUM=5

def analyze_serve(matches,name):
    serves=[]
    for m in matches:
        for s in m._sets:
            for p in s._points:
                bat=p._bats[0]
                if p._server==name:
                    if bat._fall is None:
                        strategy=bat._method
                    else:
                        strategy=bat._method+'-'+bat._fall
                    found=False
                    for s in serves:
                        if s["strategy"]==strategy:
                            s["total"]+=1
                            if(p._winner==name):
                                s["win"]+=1
                            found=True
                            break
                    if found==False:
                        serves.append({"strategy":strategy,"total":1,"win":int(p._winner==name)})
    serves=pd.DataFrame(serves).sort_values("total",ascending=False)
    plt.margins(x=0.1)
    sns.set_color_codes("pastel")

    sns.barplot(x="total", y="strategy", data=serves,
                label="Total", color="b")

    sns.set_color_codes("muted")
    sns.barplot(x="win", y="strategy", data=serves,
                label="Win", color="b")
    plt.legend(loc="lower right")
    plt.xlabel("Win/Total")
    plt.title("the serve of "+name)
    for i,(index,row) in zip(range(len(serves)),serves.iterrows()):
        #print(row.strategy,row.total,row.win,str(row.win/row.total),index)
        plt.text(row.total,i,str(round(row.win/row.total,3)),color="black",ha='left')
    #plt.show()
    if not os.path.exists("img"):
        os.mkdir("img")
    plt.savefig(os.path.join("img","serve_"+name+".png"))
    plt.clf()

def analyze_receive(matches,name):
    serves=[]
    for m in matches:
        for s in m._sets:
            for p in s._points:
                bat=p._bats[0]
                if p._server==another(name):
                    if bat._fall is None:
                        strategy=bat._method
                    else:
                        strategy=bat._method+'-'+bat._fall
                    if (name=="fan" and strategy in["a-B1","a-C1","a-A1","a-C2","a-B2"]) or \
                        name=="ma" and strategy in["b-A1","b-B1","c-B1","c-C1","a-B1"]:
                        if(len(p._bats)<2):
                            continue
                        anti_bat=p._bats[1]
                        if anti_bat._fall is None:
                            anti_strategy = anti_bat._method
                        else:
                            anti_strategy = anti_bat._method + '-' + anti_bat._fall
                        found=False
                        for s in serves:
                            if s["strategy"]==strategy and s["antistrategy"]==anti_strategy:
                                s["total"]+=1
                                if(p._winner==name):
                                    s["win"]+=1
                                found=True
                                break
                        if found==False:
                            serves.append({"strategy":strategy,"antistrategy":anti_strategy,"total":1,"win":int(p._winner==name)})
    serves=pd.DataFrame(serves)
    serves=serves[serves.total>4]
    ax=sns.barplot(x="strategy", y="total", hue="antistrategy", data=serves,palette="pastel")
    h, l = ax.get_legend_handles_labels()
    sns.barplot(x="strategy", y="win",hue="antistrategy", data=serves,palette="muted",ax=ax)
    plt.xlabel("The serve of "+another(name))
    plt.title("The receive of "+name)
    if not os.path.exists("img"):
        os.mkdir("img")
    ax.legend(loc="upper right")

    plt.tight_layout()
    plt.savefig(os.path.join("img","receive_"+name+".png"))
    plt.clf()

def analyze_combo2(matches,name):
    serves = []
    for m in matches:
        for s in m._sets:
            for p in s._points:
                last=None
                for i in range(len(p._bats)):
                    if (p._server==name and (i%2)==0)or(p._server==another(name) and (i%2)==1):
                        bat = p._bats[i]
                        if last is not None:
                            s1=extract(last)
                            s2=extract(p._bats[i-1])
                            s3=extract(bat)
                            strategy=s1+">"+s2+">"+s3
                            found = False
                            for s in serves:
                                if s["strategy"] == strategy:
                                    s["total"] += 1
                                    if (p._winner == name):
                                        s["win"] += 1
                                    found = True
                                    break
                            if found == False:
                                serves.append({"strategy": strategy, "total": 1,
                                               "win": int(p._winner == name)})
                        last=bat

    serves = pd.DataFrame(serves).sort_values("total", ascending=False)
    serves=serves[serves.total>5]
    plt.margins(x=0.1)
    sns.set_color_codes("pastel")

    sns.barplot(x="total", y="strategy", data=serves,
                label="Total", color="b")

    sns.set_color_codes("muted")
    sns.barplot(x="win", y="strategy", data=serves,
                label="Win", color="b")
    plt.legend(loc="lower right")
    plt.xlabel("Win/Total")
    plt.title("the serve of " + name)
    for i, (index, row) in zip(range(len(serves)), serves.iterrows()):
        # print(row.strategy,row.total,row.win,str(row.win/row.total),index)
        plt.text(row.total, i, str(round(row.win / row.total, 3)), color="black", ha='left')
    # plt.show()
    if not os.path.exists("img"):
        os.mkdir("img")
    plt.tight_layout()
    yint = []
    locs, labels = plt.yticks()
    for each in locs:
        yint.append(int(each))
    plt.yticks(yint)
    plt.savefig(os.path.join("img", "combo2_" + name + ".png"))
    plt.clf()

def analyze():
    matches=[]
    for i in range(NUM):
        d=getdata(i)
        matches.append(d)
    analyze_serve(matches,'ma')
    analyze_serve(matches,'fan')
    analyze_receive(matches,'ma')
    analyze_receive(matches,'fan')
    analyze_combo2(matches,'ma')
    analyze_combo2(matches,'fan')
    lp_predict(matches)

if __name__=="__main__":
    analyze()